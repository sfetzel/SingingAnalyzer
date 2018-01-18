DIRECTORY="$1"
OUTPUTDIR="$2"

for file in "$DIRECTORY"/*.flac; do
	python Spectrogram.py "$file" "$OUTPUTDIR"
done
