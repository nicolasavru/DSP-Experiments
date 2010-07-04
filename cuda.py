import numpy as np
import Image

import struct
import math

import pycuda.autoinit
import pycuda.driver as drv
import pycuda.gpuarray as gpuarray
import pycuda.cumath as cm
from pycuda.compiler import SourceModule

def oscillator(x, freq=1, amp=1, base=0, phase=0):
    return base + amp * cm.sin(2 * np.pi * freq * x + phase)

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

    # .wav header: 30 s at 44100 Hz, 1 channel of 16 bit signed samples
#    wave.write('RIFF\x14`(\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D'
#               '\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\xf0_(\x00')

                                                             #little endian
    # write float64 data as signed int16
    #amplitude/volume, max value is 32768
    #higher amplitude causes noise (vertical bars)
#    (0.01 * data).astype(np.int16).tofile(wave)
    (1000 * data).astype(np.int16).tofile(wave)

    wave.close()

#im = Image.open("reddit.jpg")
im = Image.open("fract.jpg")
#im = Image.open("test3.png")
size = im.size
d = list(im.getdata())

xres = size[0]
yres = size[1]
yscale = 22000 / float(yres)
time = int(round(22.0 * xres / yres))
#print time
xlen = time / float(size[0])
#print xlen

#initialize out to a 0
out = np.zeros(0)

r=0
g=1
b=2

for x in range(xres):
    t_gpu = gpuarray.arange(x*xlen, x*xlen + xlen, 1./44100, dtype=np.float32)
    tone_gpu = gpuarray.zeros(t_gpu.size, dtype=np.float32)
    print "{0}%".format(round(100.0 * x / xres, 2))
    for y in range(yres):
        p = d[x+xres*y]
        #keep playing with these values
        amplitude = 10**(1-5.25+4.25*(p[r]+p[g]+p[b])/(255*3))
#        print amplitude, math.log(amplitude+1)
#        amplitude = math.log(amplitude+1)# / math.log(255)
#        print x, y, amplitude
        if p[r] > 10 or p[g] > 10 and p[b] > 10:
            tone_gpu += oscillator(t_gpu,
                                   amp = amplitude,
                                   #amp=(p[r]+p[g]+p[b]),
                                   freq=yscale * (yres - y))
    tone_gpu = tone_gpu + 1
#    cm.log10(tone_gpu)
#    cm.log10(tone_gpu)
#    cm.log10(tone_gpu)
#    cm.log10(tone_gpu)
#    cm.log10(tone_gpu)
    cm.log(tone_gpu)
    tone_gpu = tone_gpu / math.log(128) #not much faster than multiple logs
    tone = tone_gpu.get()
    out = np.append(out,tone)

#pad with silence at end if necessary
if out.size < 44100 * time:
    out = np.append(out, np.zeros(44100 * time - out.size))
#print out.size

writewav('spam.wav', 1, 44100, 16, time, out)
