# Audio Video Merge

A simple Python script that merges any video file with any audio file using ffmpeg — no manual ffmpeg commands needed.

## Example Files
 
The sample video/audio files used during testing are too large to include in this GitHub repo. You can access them here:
 
🔗 **Google Drive:** [[Google Drive link ](https://drive.google.com/drive/folders/1bzvtio_HpYXaywycqFY-moynAdln9nu8?usp=drive_link)]
 
> Note: GitHub has a 100MB file size limit (25MB via the web upload UI), so large media files are intentionally excluded via `.gitignore` and hosted externally instead.

## Features

- Native file-picker dialogs to select your video and audio files from anywhere on your computer
- Supports a wide range of video formats: `.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`, `.wmv`, `.flv`, `.3gp`, `.ts`, `.mpg`, `.mpeg`, `.vob`, `.mxf`, and more
- Supports a wide range of audio formats: `.mp3`, `.wav`, `.aac`, `.flac`, `.m4a`, `.wma`, `.ogg`, `.opus`, `.aiff`, `.ac3`, `.amr`, and more
- Keeps original video quality (no re-encoding of video — fast, lossless copy)
- Converts audio to AAC for broad compatibility
- Clean progress bar with ETA instead of raw ffmpeg logs
- No need to install ffmpeg separately — bundled via `imageio-ffmpeg`

## Requirements

- Python 3.8+
- `imageio-ffmpeg` package

## Installation

```bash
git clone https://github.com/<your-username>/audio-video-merge.git
cd audio-video-merge
pip install -r requirements.txt
```

## Usage

```bash
python merge_audio_video.py
```

1. A file dialog opens — select your video file.
2. A file dialog opens — select your audio file.
3. Type a name for the merged output file (or press Enter for the default `output.mp4`).
4. The merged file is saved in the current folder.

## How it works

The script uses `ffmpeg` (via `imageio-ffmpeg`) to:
- Copy the video stream as-is (`-c:v copy`) for zero quality loss and fast processing
- Re-encode the audio track to AAC at 192kbps
- Explicitly map the video stream from the video file and the audio stream from the audio file, so the video's own original audio (if it has one) is never used by mistake
- Stop at the shorter of the two streams (`-shortest`)

## License

Feel free to use and if any changes recommeneded for better execution of code and its output please tell.
