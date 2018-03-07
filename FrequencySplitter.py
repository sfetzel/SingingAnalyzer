from __future__ import division

import numpy
import matplotlib
import matplotlib.pyplot as pyplot
import scipy.signal
from time import time
import sys
import numpy
import math
import soundfile as sf
from parabolic import parabolic

from Spectrum import *
from LpcSpectrum import *
import os

# based on: https://gist.github.com/endolith/255291
def frequencyFromAutocorrelation(sig, fs):
	"""
	Estimate frequency using autocorrelation
	"""
	# Calculate autocorrelation (same thing as convolution, but with
	# one input reversed in time), and throw away the negative lags
	corr = scipy.signal.fftconvolve(sig, sig[::-1], mode='full')
	corr = corr[len(corr)//2:]

	# Find the first low point
	d = numpy.diff(corr)
	starts = matplotlib.mlab.find(d > 0)
	frequency = 0
	
	if(starts.size > 0):
	    start = starts[0]
	    # Find the next peak after the low point (other than 0 lag).  This bit is
	    # not reliable for long signals, due to the desired peak occurring between
	    # samples, and other peaks appearing higher.
	    # Should use a weighting function to de-emphasize the peaks at longer lags.
	    peak = numpy.argmax(corr[start:]) + start
	    px, py = parabolic(corr, peak)
	    frequency = fs / px
    
	return frequency


def storeSpectrum(filename, spectrum):
	spectrumFile = open(filename + ".txt", "w+")
	for i in range(0, len(spectrum.amplitudes)):
		if(spectrum.amplitudes[i] > 0.1):
			spectrumFile.write(str(spectrum.frequencies[i]) + " " + str(spectrum.amplitudes[i]) + "\n");
	spectrumFile.close();

def storeDiagram(filename, fourierSpectrum, fourierDbSplSpectrum, fourierDbASpectrum, lpcSpectrum, lpcDbSplSpectrum, lpcDbASpectrum, title):

	figure, axesArray = pyplot.subplots(3, sharex=True)
	figure.set_figwidth(14);
	figure.set_figheight(10);
	
	axesArray[0].plot(fourierSpectrum.frequencies, fourierSpectrum.amplitudes);
	axesArray[0].plot(lpcSpectrum.frequencies, lpcSpectrum.amplitudes);
	formantIndexes = lpcSpectrum.getFormantIndexes();
	axesArray[0].plot(lpcSpectrum.formants, lpcSpectrum.amplitudes[formantIndexes], marker='o', color='r', ls='');
	axesArray[0].set_ylabel("raw")
	axesArray[0].legend(["FFT", "LPC", "LPC formants"])
	
	axesArray[1].plot(fourierDbSplSpectrum.frequencies, fourierDbSplSpectrum.amplitudes);
	axesArray[1].plot(lpcDbSplSpectrum.frequencies, lpcDbSplSpectrum.amplitudes);
	axesArray[1].plot(lpcSpectrum.formants, lpcDbSplSpectrum.amplitudes[formantIndexes], marker='o', color='r', ls='');
	axesArray[1].set_ylim(0, 150)
	axesArray[1].set_ylabel("dB(SPL)")
	axesArray[1].legend(["FFT", "LPC", "LPC formants"])
	
	axesArray[2].plot(fourierDbASpectrum.frequencies, fourierDbASpectrum.amplitudes);
	axesArray[2].plot(lpcDbASpectrum.frequencies, lpcDbASpectrum.amplitudes);
	axesArray[2].plot(lpcSpectrum.formants, lpcDbASpectrum.amplitudes[formantIndexes], marker='o', color='r', ls='');
	axesArray[2].set_ylim(0, 150)
	axesArray[2].set_ylabel("dB(A)")
	axesArray[2].legend(["FFT", "LPC", "LPC formants"])

	axesArray[0].set_title(title);
	#axesArray[0].set_xscale('log');
	axesArray[0].set_xlim(50, 7000);
	
	pyplot.savefig(filename + ".png");
	pyplot.close();



filename = sys.argv[1]
outputFolder = os.path.basename(filename)

if(len(sys.argv) > 2):
	outputFolder = sys.argv[2];

if(os.path.isdir(outputFolder) == False):
	os.makedirs(outputFolder)


print 'Reading file "%s"' % filename
signal, samplingRate = sf.read(filename)

print "Samplerate is [Hz] %f" % samplingRate;

# fs is the samplerate
# we want to measure the frequency of only 0,2s
partTimeLength = 0.2;
dataPointCount = int(samplingRate * partTimeLength);

# but then we want to have parts, which allow a FFT with high quality, how many parts?
fftSize = 65536;
partsCount = int(math.ceil(fftSize / samplingRate / partTimeLength));

print "%i parts needed for %i data points" % (partsCount, fftSize);
print "------";

frequencies = [];

for position in range(0, len(signal), dataPointCount):

	partOfSignal = signal[position:position + dataPointCount];

	frequency = frequencyFromAutocorrelation(partOfSignal, samplingRate);
	frequencies.append(frequency);

	#sys.stdout.write("From " + str(position/fs) + "s to " + str((position+dataPointCount)/fs) + "s: ");
	#sys.stdout.write('autocorrelation: %f Hz' % frequency + "\n");


diagramHarmonicFrequencies = []
harmonicRelativeAmplitude = []

diagramSingingFormantFrequencies = []
singingFormantRelativeAmplitude = []

diagramFormantsFrequency = []
diagramFormantsFormant = []

position = 0
while position < len(frequencies):
	
	frequenciesOfThisPart = frequencies[position:(position + partsCount)];
	standardDeviation = numpy.std(frequenciesOfThisPart);
	meanFrequency = numpy.mean(frequenciesOfThisPart); 
		
	# if standard deviation is less than two Hz, the passage is quite good
	# also frequency should not be below 40 and over 3000
	if standardDeviation < 1.4 and meanFrequency >= 50 and meanFrequency <= 3000:

		signalPart = signal[dataPointCount*position:dataPointCount*(position + partsCount)];
		#print "-Found passage from %d to %d s with mean frequency of %f" % (position*partTimeLength, (position+partsCount)*partTimeLength, meanFrequency)
		
		try:
			lpcSpectrum = LpcSpectrum.getByLpc(signalPart, samplingRate);
			lpcDbASpectrum = lpcSpectrum.toDbASpectrum();
			lpcDbSplSpectrum = lpcSpectrum.toDbSplSpectrum();
			
			fourierSpectrum = Spectrum.getByFft(signalPart, samplingRate);
			fourierDbSplSpectrum = fourierSpectrum.toDbSplSpectrum()
			fourierDbASpectrum = fourierSpectrum.toDbASpectrum()
			
			peakFrequencies = fourierSpectrum.getLocalMaxima(samplingRate /len(signalPart), minimumFrequencyDistance = meanFrequency/4)

			if(max(lpcDbASpectrum.amplitudes) > 30 and len(peakFrequencies) > 2):
				baseFrequency = peakFrequencies[0]
				filename = outputFolder + "/" + str(round(baseFrequency, 2));
	
				# store part in flac file
				#sf.write(filename + ".flac", signalPart, samplingRate)
				#storeSpectrum(filename, fourierDbSplSpectrum);
				
				# diagram
				storeDiagram(filename, fourierSpectrum, fourierDbSplSpectrum, fourierDbASpectrum, lpcSpectrum, lpcDbSplSpectrum, lpcDbASpectrum,
					str(baseFrequency) + " Hz ");
	
				formantIndexes = lpcDbASpectrum.getFormantIndexes();
				#singingFormantCadidatesIndex = numpy.array(numpy.argmin((abs(lpcSpectrum.formants-3000) > 2000) & (lpcSpectrum.formants < 3500))).flatten();
				
				index = -1
				baseFrequencyAmplitude = -10
				while(baseFrequencyAmplitude < 0):
					index += 1
					# due to extreme high amplitudes at the first formant,
					# which do not occur regularly, it is better to
					# use the amplitude next to the formant. Otherwise
					# it seems like the singing formant is very low for singers
					# although just the baseFrequencyAmplitude is extreme high.
					baseFrequencyAmplitude = lpcDbASpectrum.amplitudes[formantIndexes[index]+1];
				
				for index in range(index, min([14, len(formantIndexes)])):
					frequency = lpcDbASpectrum.frequencies[formantIndexes[index]];
					amplitude = lpcDbASpectrum.amplitudes[formantIndexes[index]];
					relativeAmplitude = amplitude/baseFrequencyAmplitude
					
					# for formant power diagram
					if(frequency > 2000 and frequency < 3500):
						diagramSingingFormantFrequencies.append(baseFrequency)
						singingFormantRelativeAmplitude.append(relativeAmplitude)
					else:
						if(relativeAmplitude > 0.8 and relativeAmplitude < 1.6):
							diagramHarmonicFrequencies.append(baseFrequency)
							harmonicRelativeAmplitude.append(relativeAmplitude)
					
					if(relativeAmplitude > 0.8 and relativeAmplitude < 1.6):
						# for formant diagram
						diagramFormantsFrequency.append(baseFrequency)
						diagramFormantsFormant.append(frequency)

				
				
		# catch *all* exceptions
		except:
			e = sys.exc_info()[0]
			print(sys.exc_info())
			print( "<p>Error: %s</p>" % e )
			sys.exit(0)
			
				
		position += partsCount;
	else:
		position += 1;
		
	sys.stdout.write('Position: ' + str(position) + "/" + str(len(frequencies)) + "\n")


# formant power diagram
figure, axe = pyplot.subplots(1, sharex=True)
figure.set_figwidth(14);
figure.set_figheight(10);

axe.set_title(outputFolder)
axe.plot(diagramHarmonicFrequencies, harmonicRelativeAmplitude,  marker='o', color='b', ls='', alpha=0.5);
axe.plot(diagramSingingFormantFrequencies, singingFormantRelativeAmplitude,  marker='o', color='r', ls='', alpha=0.5);
axe.set_ylabel("relative amplitude")
axe.set_xlabel("frequency")

#axe.set_xscale('log');
axe.set_xlim(50, 1000);
axe.set_ylim(0.8, 1.3);

pyplot.savefig(outputFolder + "/formantsPowerDiagram.png");
pyplot.close();

# formant position diagram
figure, axe = pyplot.subplots(1, sharex=True)
figure.set_figwidth(14);
figure.set_figheight(10);

axe.set_title(outputFolder)
axe.plot(diagramFormantsFrequency, diagramFormantsFormant,  marker='o', color='b', ls='');
axe.set_ylabel("LPC-frequency")
axe.set_xlabel("lowest frequency")
axe.set_ylim(0, 10000);
axe.set_xlim(50, 1000);

pyplot.savefig(outputFolder + "/formantsRelationDiagram.png");
pyplot.close();

formantFile = open(outputFolder + "/singingFormantsPower.txt", "w");
formantFile.write("\n".join(str(e) for e in singingFormantRelativeAmplitude));
formantFile.close();

formantFile = open(outputFolder + "/otherFormantsPower.txt", "w");
formantFile.write("\n".join(str(e) for e in harmonicRelativeAmplitude));
formantFile.close();
