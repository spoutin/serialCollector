import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.websocket import WebSocketClosedError
import tornado.gen
from tornado.options import define, options
import time
import multiprocessing
import serialworker
import threading
import socket
import json
import led
 
define("port", default=8080, help="run on the given port", type=int)
 
clients = [] 

input_queue = multiprocessing.Queue()
output_queue = multiprocessing.Queue()


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class StaticFileHandler(tornado.web.RequestHandler):
    def initialize(self, path):
        self.path = path

    def get(self, filelocation):
        print self.path
        self.render('main.js')


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    lock = threading.Lock()

    def open(self):
        # print 'new connection'
        clients.append(self)
        self.write_message("connected")
        self.ping_attempts = 0
        led.turn_off()
        ping_thread = WebSocketHandler.PingThread(self, 30)
        ping_thread.start()

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        # print 'tornado received from client: %s' % json.dumps(message)
        # self.write_message('ack')
        try:
            msg = json.loads(message)
            if 'led' in msg:
                led.turn_color(msg.led)
            else:
                input_queue.put(message)
        except ValueError:
            input_queue.put(message)

    def on_close(self):
        # print 'connection closed'
        clients.remove(self)
        if len(clients) < 1:
            led.turn_yellow()

    def on_pong(self, data):
        # Reset the ping attempts
        WebSocketHandler.lock.acquire()
        self.ping_attempts = 0
        WebSocketHandler.lock.release()

    class PingThread(threading.Thread):

        def __init__(self, websocket, frequency=2.0):
            threading.Thread.__init__(self)
            self.websocket = websocket
            self.frequency = frequency
            self.go = False

        def run(self):
            self.go = True
            while self.go:
                time.sleep(self.frequency)
                if self.websocket.close_code:
                    break
                try:
                    self.websocket.ping('beep')
                    # Track the number of ping attempts
                    WebSocketHandler.lock.acquire()
                    self.websocket.ping_attempts += 1
                    WebSocketHandler.lock.release()

                except (socket.error, WebSocketClosedError):
                    # print("Heartbeat failed for WS Client")
                    self.websocket.server_terminated = True
                    break


# check the queue for pending messages, and rely that to all connected clients
def check_queue():
    while not output_queue.empty():
        message = output_queue.get()
        for c in clients:
            c.write_message(message)


if __name__ == '__main__':
    # start the serial worker in background (as a deamon)
    sp = serialworker.SerialProcess(input_queue, output_queue)
    sp.start()
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/", IndexHandler),
            (r"/static/(.*)", StaticFileHandler, {'path':  './'}),
            (r"/ws", WebSocketHandler)
        ]
    )
    httpServer = tornado.httpserver.HTTPServer(app)
    httpServer.listen(options.port)
    print "Listening on port:", options.port

    mainLoop = tornado.ioloop.IOLoop.instance()
    # adjust the scheduler_interval according to the frames sent by the serial port
    scheduler_interval = 100
    scheduler = tornado.ioloop.PeriodicCallback(check_queue, scheduler_interval, io_loop=mainLoop)
    scheduler.start()
    try:
        mainLoop.start()
    except KeyboardInterrupt:
        print "Shutting Down!!!"

