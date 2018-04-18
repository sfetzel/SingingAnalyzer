import scipy
import matplotlib.pyplot as pyplot
import sys
import numpy
from matplotlib import mlab, rcParams
from os.path import basename

try:
    import soundfile as sf
except ImportError:
    from scikits.audiolab import flacread

from pydub import AudioSegment

def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)


filename = sys.argv[1]
print "Plotting " + filename

outputDirectory = sys.argv[2]

try:
    signal, fs = sf.read(filename)
except NameError:
    signal, fs, enc = flacread(filename)

rcParams.update({'font.size': 35})

figure, axesSubplot = pyplot.subplots(1)

figure.set_figwidth(22);
figure.set_figheight(25);
axesSubplot.set_title(basename(filename))

# 32768, 65536
axesSubplot.specgram(signal, Fs=fs, NFFT=32768, window=mlab.window_hanning, scale="dB", scale_by_freq=False)
axesSubplot.set_yscale('symlog');
axesSubplot.set_ylim(100, 10000);
axesSubplot.set_yticks([50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 5000, 6000, 7000, 8000, 10000]);
axesSubplot.set_yticklabels([50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 5000, 6000, 7000, 8000, 10000]);
axesSubplot.set_ylabel("Frequenz [Hz]");
axesSubplot.set_xlabel("Zeit [s]");

pyplot.savefig(outputDirectory + "/" + basename(filename) + ".png");
pyplot.close();
