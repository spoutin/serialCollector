from blink1.blink1 import Blink1

b1 = Blink1()


def turn_red():
    b1.fade_to_color(1000, 'red')


def turn_blue():
    b1.fade_to_color(1000, 'blue')


def turn_yellow():
    b1.fade_to_color(1000, 'yellow')


def turn_off():
    b1.off()


def turn_color(color):
    if color == 'off':
        b1.off()
    else:
        b1.fade_to_color(1000, color)
