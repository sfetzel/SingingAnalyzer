import unittest
import numpy
import soundfile as sf

from SpectrumFunctions import *

class SpectrumFunctionsTest(unittest.TestCase):

	def testToDbSplSpectrum(self):
		testSpectrum = Spectrum()
		testSpectrum.frequencies = numpy.array([ 100, 200, ])
		testSpectrum.amplitudes = numpy.array([ 10e-12, 10e-11  ])
		
		dbSpectrum = testSpectrum.toDbSplSpectrum()
		
		self.assertEqual(dbSpectrum.amplitudes[0], 0)
		self.assertEqual(dbSpectrum.amplitudes[1], 20)



	def testToDbASpectrum(self):
		testSpectrum = Spectrum()
		testSpectrum.frequencies = numpy.array([ 1000, 205, ])
		testSpectrum.amplitudes = numpy.array([ 10e-12, 10e-12  ])
		
		dbSpectrum = testSpectrum.toDbASpectrum()
		
		self.assertTrue(dbSpectrum.amplitudes[0] < 0.01)
		self.assertTrue(-11 < dbSpectrum.amplitudes[1] < -9)

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
		

	def testGetByLpc(self):
		audioData, sampleRate = sf.read("test/Sinus440.wav")
		spectrum = Spectrum.getByLpc(audioData, sampleRate)
		
		# check if there is a maximum at 440 Hz
		LowestDistanceTo440Index = numpy.argmin(numpy.abs(spectrum.frequencies-440))
		AmplitudeAt440 = spectrum.amplitudes[LowestDistanceTo440Index]
		
		self.assertTrue(len(spectrum.amplitudes) > 0)
		
		# check that 440 Hz is the only maximum
		for index in range(0, len(spectrum.amplitudes)):
			self.assertTrue(spectrum.amplitudes[index]<=AmplitudeAt440)
		


if __name__ == "__main__": 
	unittest.main()
