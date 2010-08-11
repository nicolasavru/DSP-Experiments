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
print "Loading WAV..."

wav = wave.open (fname, "r")
nchannels, sampwidth, framerate, nframes, comptype, compname = wav.getparams()
frames = wav.readframes(nframes * nchannels)
out = struct.unpack_from("%dh" % nframes * nchannels, frames)
wav.close()

data = np.zeros((nchannels, nframes), np.int16)
for f in xrange(nframes*nchannels):
    data[f%nchannels][f/nchannels] = out[f] #integer division used intentionally

print "Computing Aspect Ratio..."

# set this to the number of the channel you want to use
channel = 0
time = float(nframes) / framerate
yres = int(22 * xres / time)
#yscale = float(yres) / 22000


interval = nframes / xres
print interval, nframes

screen = render.createScreen(xres, yres)

def generateColor(val):
    v = math.log(abs(val)+.001)*10

print "Generating Spectrogram..."

for x in xrange(xres):
    fft = list()
    for c in range(nchannels):
        foo = np.fft.rfft(data[c][x*interval:(x+1)*interval+10])
        fft.append([z.real for z in foo])
    print "{0}%".format(round(100.0 * x / xres, 2))
    for y in xrange(interval / 2):
        if nchannels == 3:
            c = [math.log(abs(fft[0][y])+.001)*10,
                math.log(abs(fft[1][y])+.001)*10,
                math.log(abs(fft[2][y])+.001)*10]
        else:
            c = [math.log(abs(fft[0][y])+.001)*10,
                math.log(abs(fft[0][y])+.001)*10,
                math.log(abs(fft[0][y])+.001)*10]
        render.plot(x, yres-y, c, screen)

print "Encoding Image File..."
#render.display(screen)
render.saveExtension(screen, sys.argv[2])

print "Done."
