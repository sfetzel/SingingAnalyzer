import unittest
import numpy
import soundfile as sf

from Spectrum import *
from LpcSpectrum import *

class LpcSpectrumTest(unittest.TestCase):

	def testGetByLpc(self):
		audioData, sampleRate = sf.read("test/Sinus440.wav")
		spectrum = LpcSpectrum.getByLpc(audioData, sampleRate)
		
		# check if there is a maximum at 440 Hz
		LowestDistanceTo440Index = numpy.argmin(numpy.abs(spectrum.frequencies-440))
		AmplitudeAt440 = spectrum.amplitudes[LowestDistanceTo440Index]
		
		self.assertTrue(len(spectrum.amplitudes) > 0)
		
		# check that 440 Hz is the only maximum
		for index in range(0, len(spectrum.amplitudes)):
			self.assertTrue(spectrum.amplitudes[index]<=AmplitudeAt440)




	def testGetByLpcAeTest(self):
		audioData, sampleRate = sf.read("test/ae.wav")
		spectrum = LpcSpectrum.getByLpc(audioData, sampleRate)
		
		self.assertEqual(246.2103196947499, spectrum.formants[0])
		self.assertEqual(770.7438745940917, spectrum.formants[1])
		self.assertEqual(1762.9336154740863, spectrum.formants[2])
		self.assertEqual(2420.2588439734027, spectrum.formants[3])
		self.assertEqual(3273.62527259612, spectrum.formants[4])
		


if __name__ == "__main__": 
	unittest.main()
