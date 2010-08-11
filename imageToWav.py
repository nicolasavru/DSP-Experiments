import numpy as np
import Image, struct, math, sys

"""

Usage:
    ./imageToWav.py [c|b] image_path wav_path

"""


##### DEFS AND ARGS #####

SAMPLE_RATE = 44100

YRES = 400
T_PER_COL = 0.03

ARG_IMAGE = sys.argv[2]
ARG_OUTFILE = sys.argv[3]
ARG_COLOR = False
if sys.argv[1] == "c":
    ARG_COLOR = True

CHANNELS = 1
if ARG_COLOR:
    CHANNELS = 3

#rgb aliases
R=0
G=1
B=2


##### FUNCTIONS #####

def oscillator(x, freq=1, amp=1, base=0, phase=0):
    return base + amp * np.sin(2 * np.pi * freq * x + phase)

def writewav(filename, numChannels, sampleRate, bitsPerSample, nSamples, data):
    wave = open(filename, 'wb')
    dataSize = nSamples *  numChannels * bitsPerSample / 8
    #https://ccrma.stanford.edu/courses/422/projects/WaveFormat/
    ChunkID = 'RIFF'
    ChunkSize = struct.pack('<I', dataSize + 36)
    Format = 'WAVE'
    Subchunk1ID = 'fmt '
    Subchunk1Size = struct.pack('<I', 16)
    AudioFormat = struct.pack('<H', 1)
    NumChannels = struct.pack('<H', numChannels)
    SampleRate = struct.pack('<I', sampleRate)
    ByteRate = struct.pack('<I', sampleRate * numChannels * bitsPerSample / 8)
    BlockAlign = struct.pack('<H', numChannels * bitsPerSample / 8)
    BitsPerSample = struct.pack('<H', bitsPerSample)
    Subchunk2ID = 'data'
    Subchunk2Size = struct.pack('<I', dataSize)
    header = ChunkID + ChunkSize + Format + Subchunk1ID + Subchunk1Size +\
             AudioFormat + NumChannels + SampleRate + ByteRate + BlockAlign +\
             BitsPerSample + Subchunk2ID + Subchunk2Size
    wave.write(header)
    # higher amplitude causes noise (vertical bars)
    print "Packing WAV..."
    (1000 * data).astype(np.int16).tofile(wave)
    wave.close()


##### MAIN ROUTINE #####

# Open image and extract pixel data
im = Image.open(ARG_IMAGE)
xres = im.size[0]
yres = im.size[1]
# resize to 500px height for convenience
im = im.resize((int((float(xres)/yres)*YRES), YRES), Image.BICUBIC)
d = list(im.getdata())

# either the column width or the song length must be fixed width
# and if song length is fixed, we have to limit the frequency
# spectrum we use to maintain aspect ratio
xres = im.size[0]
yres = im.size[1]
yscale = 22000 / float(yres)
# 1/100 of a second of audio for every column in image
sampsPerCol = int(SAMPLE_RATE*T_PER_COL)


#because this is easier than finding the flag to disable broadcasting
out = [np.zeros(0), np.zeros(0), np.zeros(0)] #more mehh
elfMagic = (float(sampsPerCol)/SAMPLE_RATE)
for x in xrange(xres):
    t = np.linspace(x*elfMagic, (x+1)*elfMagic, num=sampsPerCol)
    tones = [np.zeros(sampsPerCol), np.zeros(sampsPerCol), np.zeros(sampsPerCol)] # mehh
    print "{0}: {1}%".format("Color" if ARG_COLOR else "Grayscale",
                             round(100.0 * x / xres, 2))
    for y in xrange(yres):
        p = d[x+xres*y]
        for c in range(CHANNELS):
            if p[c] > 10 or p[R] > 10 or p[G] > 10 or p[B] > 10:
                if ARG_COLOR:
                    amplitude = 10**(1-5.25+4.25*(p[c])/(255))
                else:
                    amplitude = 10**(1-5.25+4.25*(p[R]+p[G]+p[B])/(255*3))
                tones[c] += oscillator(t, amp=amplitude, freq=yscale * (yres - y))
    for c in range(CHANNELS):
        tones[c] = tones[c] + 1
        tones[c] = tones[c] / math.log(128)
        out[c] = np.append(out[c],tones[c])


if ARG_COLOR:
    out = np.array(out)
    out = out.flatten('F')
else:
    out = out[0]

writewav(ARG_OUTFILE, CHANNELS, SAMPLE_RATE, 16, int(xres*sampsPerCol), out)
