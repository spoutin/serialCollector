import subprocess


def turn_red():
    run(["blink1-tool", "--red"])


def turn_blue():
    run(["blink1-tool", "--blue"])


def turn_yellow():
    run(["blink1-tool", "--yellow"])


def turn_off():
    run(["blink1-tool", "--off"])


def turn_color(color):
    if color == 'off':
        turn_off()
    else:
        run(["blink1-tool", "--"+color])


def run(cmd):
    proc = subprocess.Popen(cmd,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            )
    proc.communicate()
