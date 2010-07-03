import numpy as np
import Image


def oscillator(x, freq=1, amp=1, base=0, phase=0):
    return base + amp * np.sin(2 * np.pi * freq * x + phase)

def writewav(filename, data):
    wave = open(filename, 'wb')

    # .wav header: 30 s at 44100 Hz, 1 channel of 16 bit signed samples
    wave.write('RIFF\x14`(\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D'
               '\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\xf0_(\x00')

    # write float64 data as signed int16
#    (32767 * data).astype(np.int16).tofile(wave)
    (8192 * data).astype(np.int16).tofile(wave)

    wave.close()

im = Image.open("test5.png")
size = im.size
d = list(im.getdata())
#print d
#print len(d)
#print size
out = oscillator(0, freq=1000)
print out
xlen = 30 / float(size[0])
#print xlen
def magnitude(pixel):
    return np.sqrt(pixel[0]**2 + pixel[1]**2 + pixel[2]**2)

xres = size[0]
yres = size[1]

for x in range(xres):
    print x, x*xlen, x*xlen + xlen
    t = np.arange(x*xlen, x*xlen + xlen, 1./44100)
    tone = np.zeros(t.size)
    yp = 0
    for y in range(yres):
        if magnitude(d[x+xres*y]) > 100 and y - yp > 1:
            print x+xres*y, "({0}, {1})".format(x, y),\
                  d[x+xres*y], magnitude(d[x+xres*y]), 200*(yres-y)
            yp = y
            tone = np.add(tone, oscillator(t, freq=200*(yres - y)))
#    print tone
    out = np.append(out,tone)
#    print out, out.size
print out.size
t = np.arange(0, 10, 1./44100)
#freq = oscillator(t, freq=6, amp=15, base=1000)
#tone = oscillator(t, freq=freq, amp=0.1)
tone = oscillator(t, freq=1000)
t = np.arange(10, 20, 1./44100)
#tone = np.add(tone, oscillator(t, freq=5000))
tone = np.append(tone, oscillator(t, freq=10000))
t = np.arange(20, 30, 1./44100)
tone = np.append(tone, oscillator(t, freq=15000))
#tone = np.add(tone, oscillator(t, freq=440))
print tone.size

writewav('spam.wav', out)
writewav('spam2.wav', tone)
