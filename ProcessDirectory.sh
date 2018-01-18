#!/bin/sh
# first argument should be directory

DIRECTORY="$1"
OUTPUTDIR="$2"

if [ -d "$DIRECTORY" ]; then
	for audioFilePath in "$DIRECTORY"/*.flac
	do
		echo "Processing $audioFilePath"
		audioFilename=$(basename "$audioFilePath")
		filenameWithoutExtension="${audioFilename%.*}"
		python FrequencySplitter.py "$audioFilePath" "-$filenameWithoutExtension" "$OUTPUTDIR"
	done
	
else
	echo "Please provide a directory with flac files as first argument"
fi
