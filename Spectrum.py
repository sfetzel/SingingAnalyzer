import numpy
import copy
import math
import scipy.signal
import scikits.talkbox
import peakutils

# reference for decibel calculation, in audio files, the maximum
# value is 1
#p0 = 2e-5
p0 = 1

class Spectrum(object):


	def _get_frequencies(self):
		return self.__frequencies
		
	def _set_frequencies(self, value):
		if not isinstance(value, numpy.ndarray):
			raise TypeError("frequencies must be a numpy ndarray")
		self.__frequencies = value
	
	frequencies = property(_get_frequencies, _set_frequencies)



	def _get_amplitudes(self):
		return self.__amplitudes
		
	def _set_amplitudes(self, value):
		if not isinstance(value, numpy.ndarray):
			raise TypeError("amplitudes must be a numpy ndarray")
		self.__amplitudes = value
	
	amplitudes = property(_get_amplitudes, _set_amplitudes)



	# converts the Spectrum instance to a dB spectrum
	def toDbSplSpectrum(self, referenceValue = p0):
		newSpectrum = copy.deepcopy(self)
		
		for index in range(0, len(newSpectrum.amplitudes)):
			newSpectrum.amplitudes[index] = 20 * numpy.log10(newSpectrum.amplitudes[index]/referenceValue)
		
		return newSpectrum
		


	# converts the Spectrum instance to a A-weighted dB spectrum
	def toDbASpectrum(self, referenceValue = p0):
		newSpectrum = copy.deepcopy(self)
		
		for index in range(0, len(newSpectrum.amplitudes)):
			# to use float 64 is necessary for the calculations
			frequency = numpy.float64(newSpectrum.frequencies[index])
			amplitude = newSpectrum.amplitudes[index];
			
			# to avoid errors, do not change infinity values
			if(amplitude != numpy.inf and amplitude > 0 and frequency > 0):
				# according to https://en.wikipedia.org/wiki/A-weighting#A / the standards
				rAatF = (numpy.float64(12194)**2 * frequency**4)/( (frequency**2 + 20.6**2 ) * math.sqrt((frequency**2+107.7**2)*(frequency**2+737.9**2)) * (frequency**2 + 12194**2) )
				newSpectrum.amplitudes[index] = 20 * numpy.log10(rAatF*amplitude/referenceValue) + 2

		return newSpectrum



	@staticmethod
	def getByFft(audioData, samplingRate):
		spectrum = Spectrum()
		
		windowed = audioData * scipy.signal.hanning(len(audioData))
		spectrum.amplitudes = numpy.abs(numpy.fft.rfft(windowed))
		spectrum.frequencies = numpy.array([index * numpy.float64(samplingRate) / len(audioData) for index in range(0, len(spectrum.amplitudes))]);
		
		return spectrum





	# to get from index to frequency the formula index * samplingRate /len(signalPart)
	# is used
	def getLocalMaxima(self, indexScaling, minimumFrequencyDistance = 1, cutLowFrequencies = True):
		peakIndices = peakutils.indexes(self.amplitudes, thres=0.02, min_dist=round(minimumFrequencyDistance))

		peakInterpolatedIndices = peakutils.interpolate(numpy.array(range(0, len(self.amplitudes))), self.amplitudes, ind=peakIndices)
		peakFrequencies = [ x * indexScaling for x in peakInterpolatedIndices];

		if(cutLowFrequencies and len(peakFrequencies) > 2):
			# cut very low frequencies which cannot be from singing
			if(peakFrequencies[0] < 50):
				peakFrequencies = peakFrequencies[1:]
				peakIndices = peakIndices[1:]
		
		return peakFrequencies

