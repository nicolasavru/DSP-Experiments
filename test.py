import numpy as np
import Image
import struct


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

    # .wav header: 30 s at 44100 Hz, 1 channel of 16 bit signed samples
#    wave.write('RIFF\x14`(\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D'
#               '\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\xf0_(\x00')

                                                             #little endian
    # write float64 data as signed int16
    #amplitude/volume, max value is 32768
    #higher amplitude causes noise (vertical bars)
    (.1 * data).astype(np.int16).tofile(wave)

    wave.close()

im = Image.open("fract.jpg")
size = im.size
d = list(im.getdata())
#print d
#print len(d)
#print size

xres = size[0]
yres = size[1]
time = 10 * int(round(22.5 * xres / yres))
#print time
xlen = time / float(size[0])
#print xlen

#initialize out to a 0
out = oscillator(0, freq=1000)

for x in range(xres):
#    print x, x*xlen, x*xlen + xlen
    t = np.arange(x*xlen, x*xlen + xlen, 1./44100)
    tone = np.zeros(t.size)
    for y in range(yres):
        p = d[x+xres*y]
        print x+xres*y, "({0}, {1})".format(x, y),\
              d[x+xres*y], 22000 / yres * (yres - y),\
              (p[0] + p[1] + p[2]), 10**((p[0]+p[1]+p[2])/(255 * 3.0))


        tone = np.add(tone, oscillator(t,
                                       amp=10**(1 + (p[0]+p[1]+p[2])/(255)),
                                       freq=22000 / yres * (yres - y)))
    out = np.append(out,tone)

#    print out, out.size
#pad with silence at end if necessary
if out.size < 44100 * time:
    out = np.append(out, np.zeros(44100 * time - out.size))
#print out.size

#constant tone experiments
#t = np.arange(0, 10, 1./44100)
#freq = oscillator(t, freq=6, amp=15, base=1000)
#tone = oscillator(t, freq=freq, amp=0.1)
#tone = oscillator(t, freq=1000)
#t = np.arange(10, 20, 1./44100)
#tone = np.add(tone, oscillator(t, freq=5000))
#tone = np.append(tone, oscillator(t, freq=10000))
#t = np.arange(20, 30, 1./44100)
#tone = np.append(tone, oscillator(t, freq=15000))
#tone = np.add(tone, oscillator(t, freq=440))
#print tone.size

writewav('spam.wav', 1, 44100, 16, time, out)
#writewav('spam2.wav', tone)
