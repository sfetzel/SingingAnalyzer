import unittest
import numpy
import soundfile as sf

from Spectrum import *

class SpectrumTest(unittest.TestCase):

	def testToDbSplSpectrum(self):
		testSpectrum = Spectrum()
		testSpectrum.frequencies = numpy.array([ 100, 200, ])
		testSpectrum.amplitudes = numpy.array([ p0, p0*10  ])
		
		dbSpectrum = testSpectrum.toDbSplSpectrum()
		
		self.assertEqual(dbSpectrum.amplitudes[0], 0)
		self.assertEqual(dbSpectrum.amplitudes[1], 20)



	def testToDbASpectrum(self):
		testSpectrum = Spectrum()
		testSpectrum.frequencies = numpy.array([ 1000, 205, 123, 0 ])
		testSpectrum.amplitudes = numpy.array([ p0, p0, -numpy.inf, 132  ])
		
		dbSpectrum = testSpectrum.toDbASpectrum()
		
		self.assertTrue(dbSpectrum.amplitudes[0] < 0.01)
		self.assertTrue(-11 < dbSpectrum.amplitudes[1] < -9)
		self.assertEqual(testSpectrum.amplitudes[2], -numpy.Inf)
		self.assertEqual(testSpectrum.amplitudes[3], 132)
		self.assertEqual(testSpectrum.amplitudes[0], p0)
		self.assertEqual(testSpectrum.amplitudes[1], p0)



	def testGetByFft(self):
		audioData, sampleRate = sf.read("test/Sinus440.wav")
		spectrum = Spectrum.getByFft(audioData, sampleRate)
		
		# check if there is a maximum at 440 Hz
		LowestDistanceTo440Index = numpy.argmin(numpy.abs(spectrum.frequencies-440))
		AmplitudeAt440 = spectrum.amplitudes[LowestDistanceTo440Index]
		
		self.assertTrue(len(spectrum.amplitudes) > 0)
		
		# check that 440 Hz is the only maximum
		for index in range(0, len(spectrum.amplitudes)):
			self.assertTrue(spectrum.amplitudes[index]<=AmplitudeAt440)
		
		
		
	# compare fft results with results from audacity
	def testGetByFftAudacityComparison(self):
		audioData, sampleRate = sf.read("test/Sinus440.wav")
		spectrum = Spectrum.getByFft(audioData[:65536], sampleRate)
		
		# check if there is a maximum at 440 Hz
		LowestDistanceTo440Index = numpy.argmin(numpy.abs(spectrum.frequencies-440))
		AmplitudeAt440 = spectrum.amplitudes[LowestDistanceTo440Index]
		
		spectrumInDb = spectrum.toDbSplSpectrum(referenceValue=1);
		
		# as audacity uses a different calculation for the dB values (according
		# to source code), a comparison of the amplitudes is not possible,
		# but a comparision of frequencies is possible
		self.assertEqual(round(spectrumInDb.frequencies[LowestDistanceTo440Index], 6), 440.084839)
		self.assertEqual(round(spectrumInDb.frequencies[1], 6), 0.672913)
		self.assertEqual(round(spectrumInDb.frequencies[2], 6), 1.345825)
		
		


if __name__ == "__main__": 
	unittest.main()
