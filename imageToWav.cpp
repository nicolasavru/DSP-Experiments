/*
To compile (yes, those are backticks):

g++ imageToWav.cpp `Magick++-config --cppflags --cxxflags --ldflags --libs`


 */

#include <iostream>
#include <fstream>
#include <string>
#include <cmath>
#include <valarray>
#include <boost/math/constants/constants.hpp>
#include <Magick++.h>
using namespace std;

const int SAMPLE_RATE = 44100;
const int BITS_PER_SAMPLE = 16;

const int YRES = 400;
const double T_PER_COL = 0.03;


double oscillator(double x, double freq=1, double amp=1, double base=0, double phase=0){
    return base + amp * sin(2 * boost::math::constants::pi<double>() * freq * x + phase);
    }

void writewav(string filename, short numChannels, int sampleRate, short bitsPerSample, int nSamples, short * data){
    int dataSize = nSamples * numChannels * bitsPerSample / 8;
    cout << nSamples << " " << numChannels << " " << bitsPerSample << " " << dataSize << endl;
    string ChunkID = "RIFF";
    int ChunkSize = dataSize + 36;
    string Format = "WAVE";
    string Subchunk1ID = "fmt ";
    int Subchunk1Size = 16;
    short AudioFormat = 1;
    short NumChannels = numChannels;
    int SampleRate = sampleRate;
    int ByteRate = sampleRate * numChannels * bitsPerSample / 8;
    short BlockAlign = numChannels * bitsPerSample / 8;
    short BitsPerSample = bitsPerSample;
    string Subchunk2ID = "data";
    int Subchunk2Size = dataSize;

    ofstream outFile(filename.c_str(), ios::out | ios::binary);
    outFile.write(ChunkID.c_str(), 4);
    outFile.write((char *) &ChunkSize, 4);
    outFile.write(Format.c_str(), 4);
    outFile.write(Subchunk1ID.c_str(), 4);
    outFile.write((char *) &Subchunk1Size, 4);
    outFile.write((char *) &AudioFormat, 2);
    outFile.write((char *) &NumChannels, 2);
    outFile.write((char *) &SampleRate, 4);
    outFile.write((char *) &ByteRate, 4);
    outFile.write((char *) &BlockAlign, 2);
    outFile.write((char *) &BitsPerSample, 2);
    outFile.write(Subchunk2ID.c_str(), 4);
    outFile.write((char *) &Subchunk2Size, 4);
    outFile.write((char *) data, dataSize);


    outFile.close();
}

int main(int argc, char *argv[]){
    string ARG_IMAGE = argv[2];
    string ARG_OUTFILE = argv[3];

    // string ARG_IMAGE = argv[2];
    // string ARG_OUTFILE = argv[3];
    // bool ARG_COLOR = argv[1][0] == 'c' ? true : false;
    // int CHANNELS = ARG_COLOR ? 3 : 1;

    int CHANNELS = 1;
    bool ARG_COLOR = false;
    if(string(argv[1]) == "c"){
        ARG_COLOR = true;
        CHANNELS = 3;
    }

    int R = 0;
    int G = 1;
    int B = 2;

    Magick::Image im;
    im.read(ARG_IMAGE.c_str());
    int xres = im.size().width();
    int yres = im.size().height();
    double z = double(YRES) / yres;
    cout << z << endl;
    cout << xres << " " << yres << endl;
    im.zoom(Magick::Geometry(xres*z, yres*z));

    xres = im.size().width();
    yres = im.size().height();
    cout << xres << " " << yres << endl;
    double yscale = 22000 / (float) yres;
    double sampsPerCol = (int)(SAMPLE_RATE*T_PER_COL);

    int x, y, c, i;
    int p[3];
    int l128 = log(128);
    short *out;
    double amplitude, **tones;
    tones = new double * [CHANNELS];
    for(c = 0; c < CHANNELS; c++){
        tones[c] = new double[(int) sampsPerCol];
        for(i = 0; i < sampsPerCol; i++){
            tones[c][i] = 0;
        }
    }
    out = new short[(int) (CHANNELS * xres * sampsPerCol)];
    for(x = 0; x < xres; x++){
        cout << x << endl;
        //        printf("%s: %4.2f\n", ARG_COLOR ? "Color" : "Grayscale", 100.0 * x / xres);
        for(y = 0; y < yres; y++){
            p[R] = im.pixelColor(x, y).redQuantum()/256;
            p[G] = im.pixelColor(x, y).greenQuantum()/256;
            p[B] = im.pixelColor(x, y).blueQuantum()/256;
            //            cout << x << " " << y << endl;
            for(c = 0; c < CHANNELS; c++){
                //                if(p[c] > 10 or p[R] > 10 or p[G] > 10 or p[B] > 10){
                    if(ARG_COLOR){
                        amplitude = pow(10, 1-5.25+4.25*(p[c])/255);
                    }
                    else{
                        amplitude = pow(10, 1-5.25+4.25*(p[R]+p[G]+p[B])/(3*255));
                    }
                    //                    cout << amplitude << endl;
                    for(i = 0; i < sampsPerCol; i++){
                        tones[c][i] += 1000 * (oscillator(x*T_PER_COL+1 + i*T_PER_COL/sampsPerCol, yscale * (yres - y), amplitude))/l128;
                        //cout << x*T_PER_COL << " " << i*T_PER_COL + i*T_PER_COL/sampsPerCol << endl;
                        //cout << (oscillator(i*T_PER_COL + i*T_PER_COL/sampsPerCol, yscale * (yres - y), amplitude))/l128 << endl;
                        //cout << tones[c][i] << " " << x << " " << y << " " << c << " " << i << " " << amplitude << endl;
                    }
                    //                }
            }
        }
        for(i = 0; i < sampsPerCol; i++){
            for(c = 0; c < CHANNELS; c++){
                out[c+CHANNELS*i+(int)sampsPerCol*x] = (short) tones[c][i];
                //cout << tones[c][i] << " " << (short) tones[c][i] << endl;
                tones[c][i] = 0;
                //cout << c << " " << i << " " << x << " " << endl;
                //cout << c+CHANNELS*i+(int)sampsPerCol*x << " " << out[c+CHANNELS*i+(int)sampsPerCol*x] << endl;
            }
            //cout << out[(int)sampsPerCol*x] << endl;
        }
    }


    writewav(ARG_OUTFILE, CHANNELS, SAMPLE_RATE, BITS_PER_SAMPLE, (int) xres*sampsPerCol, out);



    // Magick::Color  pixel_sample;
    // pixel_sample = im.pixelColor(329, 357);
    // printf("%u, %u, %u\n", pixel_sample.redQuantum()/(65536/256), pixel_sample.greenQuantum()/(65536/256), pixel_sample.blueQuantum()/(65536/256));

        //    cout << argv[1] << argv[2] << argv[3] << endl;
    return 0;
}
