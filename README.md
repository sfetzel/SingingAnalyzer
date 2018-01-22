# SingingAnalyzer
This python script splits a record of a singer into parts with nearly the same frequency. It is based on different scripts, for instance:
* formant analysis: https://stackoverflow.com/questions/25107806/estimate-formants-using-lpc-in-python which includes http://de.mathworks.com/help/signal/ug/formant-estimation-with-lpc-coefficients.html
* frequency estimation: https://gist.github.com/endolith/255291

The small parts are then analyzed using a FFT and LPC.

## usage
	python FrequencySplitter.py AudioFile.flac
To read the audio file the soundfile library is used. So you can use different types of audio files.
