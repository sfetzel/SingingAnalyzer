# based on: https://gist.github.com/endolith/255291


from __future__ import division
from numpy.fft import rfft
from numpy import argmax, mean, diff, log, array, std, linspace, arange, append
from matplotlib.mlab import find
import matplotlib.pyplot as pyplot
from scipy.signal import blackmanharris, fftconvolve, hanning
import peakutils
from time import time
import sys
import numpy
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


def store_fouriertransformation(filename, fourierTransform, signalPartLength):
	spectrumFile = open(filename + ".txt", "w+")
	for i in range(0, len(fourierTransform)):
		if(fourierTransform[i] > 0.1):
			frequency = fs * i / signalPartLength
			spectrumFile.write(str(frequency) + " " + str(fourierTransform[i]) + "\n");
	spectrumFile.close();

def store_diagram(filename, x, dbASpectrum, fourierTransform, title):
	figure, axesArray = pyplot.subplots(2, sharex=True)
	figure.set_figwidth(14);
	
	axesArray[0].plot(x, fourierTransform);
	axesArray[0].set_ylabel("raw")
	
	axesArray[1].plot(x, dbASpectrum);
	axesArray[1].set_ylim(-10, 80);
	axesArray[1].set_ylabel("dB(A)")

	axesArray[0].set_title(title);
	axesArray[0].set_xscale('log');
	axesArray[0].set_xlim(50, 7000);
	
	pyplot.savefig(filename + ".png");
	pyplot.close();


def store_local_maximums(peakIndices, peakFrequencies, suffixForOutput):
	
	# store frequency followed by normalized absolute value
	peakFrequenciesFileAll.write(suffixForOutput);
	peakIndicesPart = peakIndices[:7];
	for i in range(0, len(peakIndicesPart)):
		index = peakIndices[i]
		peakFrequenciesFileAll.write(" " + str(peakFrequencies[i]) + " " + str(fourierTransform[index]/fourierTransform[peakIndices[0]]));
		peakFrequenciesFile.write(str(peakFrequencies[i]) + " " + str(fourierTransform[index]/fourierTransform[peakIndices[0]]) + " ");
	peakFrequenciesFile.write("\n");
	peakFrequenciesFileAll.write("\n");

filename = sys.argv[1]
suffixForOutput = "-frequency";
outputFolder = "splitted"
if(len(sys.argv) > 1):
	suffixForOutput = sys.argv[2];
if(len(sys.argv) > 2):
	outputFolder = sys.argv[3];


peakFrequenciesFileAll = open(outputFolder + "/peaks.txt", "a+")
peakFrequenciesFile = open(outputFolder + "/peaks" + suffixForOutput + ".txt", "w+")

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
	

#dbArTable = array('f');
#for frequencyIndex in range(0, 100 * 1000):
	# frequency is a tenth of the index
#	f = frequencyIndex / 10;
#	rAatF = (12194**2 * f**4)/( (f**2 + 20.6**2 ) * math.sqrt((f**2+107.7**2)*(f**2+737.9**2)) * (f**2 + 12194**2) )
#	dbArTable.append(rAatF);

	
position = 0
while position < len(frequencies):
	frequenciesOfThisPart = frequencies[position:(position + partsCount)];
	standardDeviation = std(frequenciesOfThisPart);
	meanFrequency = mean(frequenciesOfThisPart); 
		
	# if standard deviation is less than two Hz, the passage is quite good
	# also frequency should not be below 40 and over 3000
	if standardDeviation < 1.5 and meanFrequency >= 50 and meanFrequency <= 3000:


		signalPart = signal[dataPointCount*position:dataPointCount*(position + partsCount)];
		print "-Found passage from %d to %d s with mean frequency of %f" % (position*partTimeLength, (position+partsCount)*partTimeLength, meanFrequency)
		
		try:
			# get fourier transform
			windowed = signalPart * hanning(len(signalPart))
			fourierTransform = abs(rfft(windowed))
			fourierTransformIndices = range(0, len(fourierTransform));
		
			# minimum distance between maximums must be at one fourth of the base frequency
			# threshold is "Normalized threshold. Only the peaks with amplitude higher than the threshold will be detected."
			peakIndices = peakutils.indexes(fourierTransform,thres=0.02, min_dist=round(meanFrequency/4))
			peakInterpolatedIndices = peakutils.interpolate(array(fourierTransformIndices), fourierTransform, ind=peakIndices)
		
			peakFrequencies = [ x * fs /len(signalPart) for x in peakIndices];
		
			if(len(peakFrequencies) > 2):
				# cut very low frequencies which cannot be from singing
				if(peakFrequencies[0] < 50):
					peakFrequencies = peakFrequencies[1:]
					peakIndices = peakIndices[1:]

				filename = outputFolder + "/" + str(round(peakFrequencies[0])) + suffixForOutput;
		
				# store part in flac file
				sf.write(filename + ".flac", signalPart, fs)
		
		
				# store fourier transform
				#store_fouriertransformation(filename, fourierTransform, len(signalPart))
		
				# indices of fourierTransform list are not frequencies, map them
				frequencies = [index * fs / len(signalPart) for index in range(0, len(fourierTransform))];
		
				#dbASpectrum = array([])
				N = len(fourierTransform)
				dbASpectrum = numpy.empty(N)

				# transform from dB to dBA
				for index in range(0, len(fourierTransform)):
					# according to https://en.wikipedia.org/wiki/A-weighting#Function_realisation_of_some_common_weightings
					f = frequencies[index];
					if ( f > 50):
						rAatF = (12194**2 * f**4)/( (f**2 + 20.6**2 ) * math.sqrt((f**2+107.7**2)*(f**2+737.9**2)) * (f**2 + 12194**2) )
						AatF = 20 * math.log10(rAatF * fourierTransform[index]) + 2
						dbASpectrum[index] = AatF;
					else:
						dbASpectrum[index] = 0;
			
		
				#dbASpectrumMaximum = max(dbASpectrum);
				#dbASpectrumNormalized = [ x / fourierTransformMaximum for x in dbASpectrum];
		
				# diagram
				store_diagram(filename, frequencies, dbASpectrum, fourierTransform,
					str(peakFrequencies[0]) + " Hz " + suffixForOutput);
		
				# get local maximums
				#store_local_maximums(peakIndices, peakFrequencies, suffixForOutput);

		# catch *all* exceptions
		except:
			e = sys.exc_info()[0]
			print( "<p>Error: %s</p>" % e )
			
				
		position += partsCount;
	else:
		position += 1;
