import numpy as np
import Image, struct, math, sys

"""

Usage:
    ./imageToWav.py [c|b] image_path wav_path

"""


##### DEFINES AND ARGS #####

SAMPLE_RATE = 44100

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

def writewav(filename, numChannels, sampleRate, bitsPerSample, time, data):
    wave = open(filename, 'wb')
    dataSize = time * sampleRate *  numChannels * bitsPerSample / 8
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
    # wav header: 30 s at 44100 Hz, 1 channel of 16 bit signed samples
    # wave.write('RIFF\x14`(\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D'
    #            '\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\xf0_(\x00')
    # little endian
    # write float64 data as signed int16
    # amplitude/volume, max value is 32768
    # higher amplitude causes noise (vertical bars)
    print "Packing WAV..."
    (1000 * data).astype(np.int16).tofile(wave)
    wave.close()


##### MAIN ROUTINE #####

# Open image and extract pixel data
im = Image.open(ARG_IMAGE)
size = im.size
d = list(im.getdata())

xres = size[0]
yres = size[1]
yscale = 22000 / float(yres)
time = int(round(22.0 * xres / yres))
xlen = time / float(size[0])



# Initilize out
out = np.zeros(0)

if ARG_COLOR:
    for x in xrange(xres):
        t = np.arange(x*xlen, x*xlen + xlen, 1./SAMPLE_RATE)
        tones = [np.zeros(t.size), np.zeros(t.size), np.zeros(t.size)] # mehh
        print "Color: {0}%".format(round(100.0 * x / xres, 2))
        for y in xrange(yres):
            p = d[x+xres*y]
            for c in range(CHANNELS):
                if p[c] > 10:
                    amplitude = 10**(1-5.25+4.25*(p[c])/(255))
                    tones[c] += oscillator(t, amp=amplitude, freq=yscale * (yres - y))
        for c in range(CHANNELS):
            tones[c] = tones[c] + 1
            tones[c] = tones[c] / math.log(128)
            out = np.append(out,tones[c])
else:
    for x in xrange(xres):
        t = np.arange(x*xlen, x*xlen + xlen, 1./SAMPLE_RATE)
        tone = np.zeros(t.size)
        print "Grayscale: {0}%".format(round(100.0 * x / xres, 2))
        for y in xrange(yres):
            p = d[x+xres*y]
            if p[R] > 10 or p[G] > 10 and p[B] > 10:
                # keep playing with these values
                # print amplitude, math.log(amplitude+1)
                # amplitude = math.log(amplitude+1)# / math.log(255)
                # print x, y, amplitude
                amplitude = 10**(1-5.25+4.25*(p[R]+p[G]+p[B])/(255*3))
                tone += oscillator(t, amp=amplitude, freq=yscale * (yres - y))
        tone = tone + 1
        tone = tone / math.log(128)
        out = np.append(out,tone)

#pad with silence at end if necessary
if out.size < SAMPLE_RATE * time:
    out = np.append(out, np.zeros(SAMPLE_RATE * time - out.size))

writewav(ARG_OUTFILE, CHANNELS, SAMPLE_RATE, 16, time, out)
