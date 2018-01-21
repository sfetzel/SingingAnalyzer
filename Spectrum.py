import numpy
import copy
import math
import scipy.signal
import scikits.talkbox

# reference for decibel calculation
p0 = 2e-5
#p0 = 10e-12

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
		newSpectrum = Spectrum()
		newSpectrum.frequencies = copy.copy(self.frequencies)
		newSpectrum.amplitudes = copy.copy(self.amplitudes)
		
		for index in range(0, len(newSpectrum.amplitudes)):
			newSpectrum.amplitudes[index] = 20 * numpy.log10(newSpectrum.amplitudes[index]/referenceValue)
		
		return newSpectrum
		


	# converts the Spectrum instance to a A-weighted dB spectrum
	def toDbASpectrum(self):
		newSpectrum = Spectrum()
		newSpectrum.frequencies = copy.copy(self.frequencies)
		newSpectrum.amplitudes = copy.copy(self.amplitudes)
		
		for index in range(0, len(newSpectrum.amplitudes)):
			# to use float 64 is necessary for the calculations
			frequency = numpy.float64(newSpectrum.frequencies[index])
			
			# according to https://en.wikipedia.org/wiki/A-weighting#A / the standards
			rAatF = (numpy.float64(12194)**2 * frequency**4)/( (frequency**2 + 20.6**2 ) * math.sqrt((frequency**2+107.7**2)*(frequency**2+737.9**2)) * (frequency**2 + 12194**2) )
			newSpectrum.amplitudes[index] = 20 * numpy.log10(rAatF*newSpectrum.amplitudes[index]/p0) + 2
		
		return newSpectrum



	@staticmethod
	def getByFft(audioData, samplingRate):
		spectrum = Spectrum()
		
		windowed = audioData * scipy.signal.hanning(len(audioData))
		spectrum.amplitudes = numpy.abs(numpy.fft.rfft(windowed))
		spectrum.frequencies = numpy.array([index * numpy.float64(samplingRate) / len(audioData) for index in range(0, len(spectrum.amplitudes))]);
		
		return spectrum






	#def getLocalMaxima(self, minimumFrequencyDistance = 1):
		#peakIndices = peakutils.indexes(spectrum.amplitudes, thres=0.02, min_dist=minimumFrequencyDistance)
		#peakInterpolatedIndices = peakutils.interpolate(array(fourierTransformIndices), fourierTransform, ind=peakIndices)

