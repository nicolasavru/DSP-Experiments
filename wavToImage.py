"""

wavToImage.py
Creates a spectrogram image from a wav file.
Auto-detects color or grayscale.

Author: Jordan Perr-Sauer, jordan@jperr.com
        Nicolas Avrutin, nicolasavru@gmail.com

Revision history:
    See http://github.com/nicolasavru/DSP-Experiments

Bugs:
    - Scaling leaves nasty artifacts

Todo:
    - Tweak scaling/encoding algorithm to lessen artifacts
    - Variable resolution spectrogram

"""


##### IMPORTS #####

import wave, sys, struct, math, Image
import numpy as np


##### DEFS AND ARGS #####

YRES = 400
T_PER_COL = 0.03

ARG_WAVFILE = sys.argv[1]
ARG_IMGFILE = sys.argv[2]


##### MAIN ROUTINE #####

print "Loading WAV..."

# Load wav file into array
# http://stackoverflow.com/questions/2063284/what-is-the-easiest-way-to-read-wav-files-using-python-summary
wav = wave.open (ARG_WAVFILE, "r")
nchannels, sampwidth, framerate, nframes, comptype, compname = wav.getparams()
frames = wav.readframes(nframes * nchannels)
out = struct.unpack_from("%dh" % nframes * nchannels, frames)
wav.close()

# Separate loaded frames by channel
data = np.zeros((nchannels, nframes), np.int16)
for f in xrange(nframes*nchannels):
    data[f%nchannels][f/nchannels] = out[f] # integer division used intentionally

# Compute the dimensions of the encoded image
# Setup some constants for decoding
sampsPerCol = framerate*T_PER_COL
yres = YRES
xres = int(math.ceil((nframes)/sampsPerCol))

# Create a PIL Image
if nchannels == 3:
    im = Image.new("RGB", (xres+1, yres+1))
else:
    im = Image.new("L", (xres+1, yres+1))


print "Generating Spectrogram..."

# Loop over all "slices" in WAV file.
for x in xrange(xres):
    fft = list()
    # Perform an FFT on the sound contained in each slice
    for c in range(nchannels):
        foo = np.fft.rfft(data[c][x*sampsPerCol:(x+1)*sampsPerCol])
        fft.append([z.real for z in foo])
    print "{0}%".format(round(100.0 * x / xres, 2))
    # Compute pixel colors from fft result
    for y in xrange(len(fft[0])):
        if nchannels == 3:
            c = (int(math.log(abs(fft[0][y])+.001)*10),
                int(math.log(abs(fft[1][y])+.001)*10),
                int(math.log(abs(fft[2][y])+.001)*10))
        else:
            c = int(math.log(abs(fft[0][y])+.001)*10)
        # Plot pixels, scaling to YRES
        im.putpixel((int(x), int(yres-int(((float(y)/len(fft[0]))*YRES)))), c)

print "Encoding Image File..."

# Save image file using PIL
im.save(ARG_IMGFILE, ARG_IMGFILE.split(".")[-1].upper())

print "Done."
