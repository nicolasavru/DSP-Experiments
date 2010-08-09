# STDLIB
import wave
import sys
import struct
import math

import render
# Dependencies
import numpy as np

xres = 1000
yres = 1000

fname = sys.argv[1]

# http://stackoverflow.com/questions/2063284/what-is-the-easiest-way-to-read-wav-files-using-python-summary

wav = wave.open (fname, "r")
nchannels, sampwidth, framerate, nframes, comptype, compname = wav.getparams()
frames = wav.readframes(nframes * nchannels)
out = struct.unpack_from("%dh" % nframes * nchannels, frames)

sound = np.array(out)
print sound

interval = nframes / xres
print interval, nframes

screen = render.createScreen(xres, interval)#yres)

for x in range(xres):
    fft = np.fft.rfft(sound[x*interval:(x+1)*interval])
    fft = [z.real for z in fft]
    print len(fft)
#    print fft
#    print "{0}%".format(round(100.0 * x / xres, 2))
    for y in range(interval/2):
#        p = d[x+xres*y]
        c = [math.log(abs(fft[y])+.001)*10, 0, 0]#255-math.log(abs(y)+.01), 0]
        print x, y, c
        render.plot(x, y, c, screen)

#render.display(screen)
render.saveExtension(screen, "out.png")



fft = np.fft.rfft(sound)
print fft
