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
wav.close()

print nchannels, nframes
data = np.zeros((nchannels, nframes), np.int16)
for f in xrange(nframes):
    for c in xrange(nchannels):
        data[c][f] = out[f+c]

# set this to the number of the channel you want to use
channel = 0
#loadWav(fname)
interval = nframes / xres
print interval, nframes

screen = render.createScreen(xres, interval/2)

def generateColor(val):
    v = math.log(abs(val)+.001)*10

for x in range(xres):
    fft0 = np.fft.rfft(data[0][x*interval:(x+1)*interval+10])
    fft1 = np.fft.rfft(data[1][x*interval:(x+1)*interval+10])
    fft2 = np.fft.rfft(data[2][x*interval:(x+1)*interval+10])
    fft0 = [z.real for z in fft0]
    fft1 = [z.real for z in fft1]
    fft2 = [z.real for z in fft2]
#    print len(fft)
#    print fft
    print "{0}%".format(round(100.0 * x / xres, 2))
    for y in range(interval/2):
#        p = d[x+xres*y]
        c = [math.log(abs(fft0[y])+.001)*10,
            math.log(abs(fft1[y])+.001)*10,
            math.log(abs(fft2[y])+.001)*10]
        # c = [abs(fft0[y]/100),
        #      abs(fft1[y]/100),
        #      abs(fft2[y]/100)]
        print x, y, c
        render.plot(x, interval/2-y, c, screen)

#render.display(screen)
render.saveExtension(screen, sys.argv[2])
