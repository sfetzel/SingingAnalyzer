# based on: https://gist.github.com/endolith/255291


from __future__ import division
from numpy.fft import rfft
from numpy import argmax, mean, diff, log, array, std, linspace
from matplotlib.mlab import find
from scipy.signal import blackmanharris, fftconvolve, hanning
import peakutils
from time import time
import sys
import math
try:
    import soundfile as sf
except ImportError:
    from scikits.audiolab import flacread

from parabolic import parabolic


def freq_from_autocorr(sig, fs):
    """
    Estimate frequency using autocorrelation
    """
    # Calculate autocorrelation (same thing as convolution, but with
    # one input reversed in time), and throw away the negative lags
    corr = fftconvolve(sig, sig[::-1], mode='full')
    corr = corr[len(corr)//2:]

    # Find the first low point
    d = diff(corr)
    start = find(d > 0)[0]

    # Find the next peak after the low point (other than 0 lag).  This bit is
    # not reliable for long signals, due to the desired peak occurring between
    # samples, and other peaks appearing higher.
    # Should use a weighting function to de-emphasize the peaks at longer lags.
    peak = argmax(corr[start:]) + start
    px, py = parabolic(corr, peak)

    return fs / px



filename = sys.argv[1]
suffixForOutput = "-frequency";
if(len(sys.argv) > 1):
	suffixForOutput = sys.argv[2];

print 'Reading file "%s"' % filename
try:
    signal, fs = sf.read(filename)
except NameError:
    signal, fs, enc = flacread(filename)

print "Samplerate is [Hz] %f" % fs;

# fs is the samplerate
# we want to measure the frequency of only 0,2s
partTimeLength = 0.2;
dataPointCount = int(fs * partTimeLength);

# but then we want to have parts, which allow a FFT with high quality, how many parts?
fftSize = 65536;
partsCount = int(math.ceil(fftSize / fs / partTimeLength));

print "%i parts needed for %i data points" % (partsCount, fftSize);
print "------";

frequencies = [];

for position in range(0, len(signal), dataPointCount):

	partOfSignal = signal[position:position + dataPointCount];

	frequency = freq_from_autocorr(partOfSignal, fs);
	
	frequencies.append(frequency);

	sys.stdout.write("From " + str(position/fs) + "s to " + str((position+dataPointCount)/fs) + "s: ");
	sys.stdout.write('autocorrelation: %f Hz' % frequency + "\n");
	
position = 0
while position < len(frequencies):
	frequenciesOfThisPart = frequencies[position:(position + partsCount)];
	standardDeviation = std(frequenciesOfThisPart);
	meanFrequency = mean(frequenciesOfThisPart); 
		
	# if standard deviation is less than two Hz, the passage is quite good
	# also frequency should not be below 40 and over 3000
	if standardDeviation < 2 and meanFrequency >= 40 and meanFrequency <= 3000:

		signalPart = signal[dataPointCount*position:dataPointCount*(position + partsCount)];
		print "-Found passage from %d to %d s with mean frequency of %f" % (position*partTimeLength, (position+partsCount)*partTimeLength, meanFrequency)
		filename = "splitted/" + str(round(meanFrequency)) + suffixForOutput;
		sf.write(filename + ".flac", signalPart, fs)
		
		
		windowed = signalPart * hanning(len(signalPart))
		fourierTransform = abs(rfft(windowed))
		spectrumFile = open(filename + ".txt", "w+")

		# get local maximums
		fourierTransformIndices = range(0, len(fourierTransform));
		
		peakIndices = peakutils.indexes(fourierTransform)
		peakInterpolatedIndices = peakutils.interpolate(array(fourierTransformIndices), fourierTransform, ind=peakIndices)
		
		for i in range(0, len(peakIndices)):
			index = peakIndices[i]
			interpolatedIndex = peakInterpolatedIndices[i];
			print str(fs * interpolatedIndex / len(signalPart)) + " - " + str(fourierTransform[index]);
		
		
		for i in range(0, len(fourierTransform)):
			frequency = fs * i / len(signalPart)
			spectrumFile.write(str(frequency) + " " + str(fourierTransform[i]) + "\n");
		
		spectrumFile.close();
				
		position += partsCount;
	else:
		position += 1;
