import wave, sys, struct, math
import Image
import numpy as np

YRES = 300
T_PER_COL = 0.02

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


sampsPerCol = framerate*T_PER_COL
yres = YRES
xres = math.ceil((nframes)/sampsPerCol)


interval = nframes / xres
print interval, nframes

if nchannels == 3:
    im = Image.new("RGB", (xres+1, yres+1))
else:
    im = Image.new("L", (xres+1, yres+1))

print (xres, yres)

def generateColor(val):
    v = math.log(abs(val)+.001)*10

print "Generating Spectrogram..."

for x in xrange(xres):
    fft = list()
    for c in range(nchannels):
        foo = np.fft.rfft(data[c][x*sampsPerCol:(x+1)*sampsPerCol])
        fft.append([z.real for z in foo])
    print "{0}%".format(round(100.0 * x / xres, 2))
    for y in xrange(len(fft[0])):
        if nchannels == 3:
            c = (math.log(abs(fft[0][y])+.001)*10,
                math.log(abs(fft[1][y])+.001)*10,
                math.log(abs(fft[2][y])+.001)*10)
        else:
            c = math.log(abs(fft[0][y])+.001)*10
        im.putpixel((x, yres-int(((float(y)/len(fft[0]))*YRES))), c)

print "Encoding Image File..."
#render.display(screen)
im.save(sys.argv[2], sys.argv[2].split(".")[-1].upper())

print "Done."
