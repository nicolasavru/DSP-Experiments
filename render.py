import shlex
import subprocess

def createScreen(XRES, YRES):
    """
    Return [XRES]x[YRES] screen initialized to color [0,0,0].
    """
    return [[[0,0,0] for x in range(XRES)] for y in range(YRES)]

def plot(x, y, color, screen):
    """
    Set (x,y) in screen to color.
    """
    if 0 < x < len(screen[0]) and 0 < y < len(screen):
        screen[int(y)][int(x)] = [int(col) for col in color]

def display(screen):
    """
    Pipe screen to display.
    """
    p = subprocess.Popen("display", stdin=subprocess.PIPE)
    p.stdin.write("P3\n{0} {1}\n{2}\n".format(len(screen[0]), len(screen), 255))
    for y in screen:
        for x in y:
          p.stdin.write("{0} {1} {2}\n".format(x[0], x[1], x[2]))
    p.stdin.close()

def savePPM(screen, filename):
    """
    Save screen to filename.ppm.
    """
    f = open(filename, 'wb')
    f.write("P3\n{0} {1}\n{2}\n".format(len(screen[0]), len(screen), 255))

    for y in screen:
        for x in y:
          f.write("{0} {1} {2}\n".format(x[0], x[1], x[2]))
    f.close()

def saveExtension(screen, filename):
    """
    Save screen to filename. Include extension in filename.
    """
    p = subprocess.Popen(shlex.split("convert - {0}".format(filename)),
                         stdin=subprocess.PIPE)
    p.stdin.write("P3\n{0} {1}\n{2}\n".format(len(screen[0]), len(screen), 255))

    for y in screen:
        for x in y:
          p.stdin.write("{0} {1} {2}\n".format(x[0], x[1], x[2]))

if __name__ == "__main__":
    print("Run main.py to use.")
