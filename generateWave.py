import numpy
from scipy.io import wavfile
from wave import *
import struct

duration = 4 # seconds
samplerate = 44100 # Hz
samples = duration*samplerate
frequencies = [440, 880, 1660, 2000, 8000, 10000] # Hz
# in sample points
periods = [samplerate / float(freq) for freq in frequencies]
omegas = [numpy.pi * 2 / period for period in periods]

def sine_wave(x, freq=100):
    sample = numpy.arange(x*4096, (x+1)*4096, dtype=numpy.float32)
    sample *= numpy.pi * 2 / 44100
    sample *= freq
    return numpy.sin(sample)

for x in xrange(1000):
    sample = sine_wave(x, 100)
    wavfile.write

arr = numpy.fromfunction(numpy.sin, (1, samples))
print arr
sound = wavfile.read("test.wav")
print sound

wav = open('test.wav')
length = wav.getnframes()

#tmp = [struct.unpack('f', wav.readframes(1))[0] for x in range(length)]
data = numpy.fromfile('test.wav')#.reshape(-1, 2)[0]
data[numpy.isnan(data)] = 0
print data
#spectrogram = specgram(data)
#title('Spectrogram')

#show();
