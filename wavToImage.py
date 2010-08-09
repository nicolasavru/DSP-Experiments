import wave
import sys
import struct
import math

import render

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

interval = nframes / xres
print interval, nframes

screen = render.createScreen(xres, interval/2)

def generateColor(val):
    v = math.log(abs(val)+.001)*10

for x in range(xres):
#    fft = np.fft.rfft(sound[x*interval:(x+1)*interval])
    fft = np.fft.rfft(sound[x*interval:(x+1)*interval+10])
    fft = [z.real for z in fft]
#    print len(fft)
#    print fft
    print "{0}%".format(round(100.0 * x / xres, 2))
    for y in range(interval/2):
#        p = d[x+xres*y]
        c = [math.log(abs(fft[y])+.001)*10,
             math.log(abs(fft[y])+.001)*10,
             math.log(abs(fft[y])+.001)*10]
#        print x, y, c
        render.plot(xres-x, interval/2-y, c, screen)

#render.display(screen)
render.saveExtension(screen, sys.argv[2])
