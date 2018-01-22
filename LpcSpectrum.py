import math

from Spectrum import *

class LpcSpectrum(Spectrum):

	def __init__(self):
		Spectrum.__init__(self)

	def _get_formants(self):
		return self.__formants
		
	def _set_formants(self, value):
		if not isinstance(value, numpy.ndarray):
			raise TypeError("formants must be a numpy ndarray")
		self.__formants = value
	
	formants = property(_get_formants, _set_formants)

	@staticmethod
	def getByLpc(audioData, samplingRate):
		# Get Hamming window.
		window = numpy.hamming(len(audioData))

		# Apply window and high pass filter.
		audioDataWindowed = audioData * window
		audioDataFiltered = scipy.signal.lfilter([1], [1., 0.63], audioDataWindowed)

		# Get LPC. number of coefficients according to rule of thumb
		numberOfCoefficients = 2 + samplingRate / 1000
		# A are lpc coefficients
		# another example: https://qiita.com/ar90n@github/items/0611f8d4452d0ccc9151
		LpcCoefficients, e, k = scikits.talkbox.lpc(audioDataFiltered, numberOfCoefficients)

		# calculate frequency response
		# according to https://stackoverflow.com/questions/29620694/matlab-freqz-function-in-python
		w, h = scipy.signal.freqz(1, LpcCoefficients)

		spectrum = LpcSpectrum()
		spectrum.frequencies = samplingRate * w / (2*math.pi)
		spectrum.amplitudes = numpy.abs(h)
		
		# Get roots. Sort out the half because every root
		# has also the complex conjugated one
		rts = numpy.roots(LpcCoefficients)
		rts = [r for r in rts if numpy.imag(r) >= 0]

		# Get angles.
		angz = numpy.arctan2(numpy.imag(rts), numpy.real(rts))

		# Get frequencies.
		spectrum.formants = numpy.array(sorted(angz * (samplingRate / (2 * math.pi))))
		
		return spectrum
		
		
	def getFormantIndexes(self):
		return [  numpy.argmin(abs(self.frequencies-formant))  for formant in self.formants];
