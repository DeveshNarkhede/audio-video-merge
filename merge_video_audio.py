import os
import re
import time
import subprocess
import imageio_ffmpeg

VIDEO_EXTENSIONS = {
    ".mp4", ".m4v", ".mov", ".qt",
    ".mkv", ".avi", ".webm",
    ".wmv", ".flv", ".f4v",
    ".3gp", ".3g2", ".ts", ".mts", ".m2ts",
    ".mpg", ".mpeg", ".vob", ".ogv",
    ".asf", ".rm", ".rmvb", ".divx",
    ".mxf", ".y4m",
}

AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".aac",
    ".flac", ".m4a", ".wma",
    ".ogg", ".oga", ".opus",
    ".aiff", ".aif", ".alac",
    ".ac3", ".eac3", ".dts",
    ".amr", ".caf", ".mka",
    ".mpeg", ".mpa", ".mp2",
}


def validate(path, allowed, kind):
    if not path:
        raise ValueError(f"No {kind} file was selected.")

    if not os.path.exists(path):
        raise FileNotFoundError(f"{kind.capitalize()} file not found:\n{path}")

    ext = os.path.splitext(path)[1].lower()

    if ext not in allowed:
        raise ValueError(
            f"Unsupported {kind} format: '{ext}'\n"
            f"Supported {kind} formats: {', '.join(sorted(allowed))}"
        )

def _gui_available():
    try:
        import tkinter
        return True
    except Exception:
        return False


def pick_file(title, kind, allowed_exts):
    """
    Opens a native 'browse your folders/files' dialog so the user can pick
    a file from anywhere on their laptop. Falls back to a typed path if
    tkinter isn't available in the environment.
    """
    if _gui_available():
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)

            filetypes = [
                (f"{kind.capitalize()} files", " ".join(f"*{e}" for e in sorted(allowed_exts))),
                ("All files", "*.*"),
            ]

            path = filedialog.askopenfilename(title=title, filetypes=filetypes)
            root.destroy()

            if path:
                return path
            print(f"No {kind} file selected in the dialog, please type the path instead.")
        except Exception as e:
            print(f"(Could not open file dialog: {e}. Falling back to typed path.)")

    path = input(f"{title}: ").strip().strip('"')
    return path

def _get_duration_seconds(path, ffmpeg_exe):
    """Best-effort attempt to read media duration so we can show progress %."""
    try:
        result = subprocess.run(
            [ffmpeg_exe, "-i", path],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("Duration:"):
                time_str = line.split(",")[0].replace("Duration:", "").strip()
                h, m, s = time_str.split(":")
                return int(h) * 3600 + int(m) * 60 + float(s)
    except Exception:
        pass
    return None


def _format_eta(seconds):
    seconds = max(0, int(seconds))
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def merge(video_path, audio_path, output_path="output.mp4", quiet=True):

    validate(video_path, VIDEO_EXTENSIONS, "video")
    validate(audio_path, AUDIO_EXTENSIONS, "audio")

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    command = [
        ffmpeg,
        "-y",
        "-i", video_path,
        "-i", audio_path,

        "-map", "0:v:0",
        "-map", "1:a:0",

        "-c:v", "copy",

        "-c:a", "aac",
        "-b:a", "192k",

        "-shortest",
    ]

    if quiet:
        command += ["-hide_banner", "-loglevel", "error", "-stats"]

    command.append(output_path)

    if not quiet:
        subprocess.run(command, check=True)
    else:
        print("Merging... this may take a moment.")
        duration = _get_duration_seconds(video_path, ffmpeg)

        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        start_time = time.time()
        time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")

        for line in process.stdout:
            match = time_pattern.search(line)
            if match and duration:
                h, m, s = match.groups()
                elapsed_in_video = int(h) * 3600 + int(m) * 60 + float(s)
                percent = min(100, (elapsed_in_video / duration) * 100)
                elapsed_real = time.time() - start_time
                eta = (elapsed_real / percent * (100 - percent)) if percent > 0 else 0
                print(f"\rProgress: {percent:5.1f}%  ETA: {_format_eta(eta)}   ", end="", flush=True)

        process.wait()
        print()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)

    print("\n✅ Done!")
    print("Saved to:", os.path.abspath(output_path))

if __name__ == "__main__":

    print("Select your video file...")
    video = pick_file("Select video file", "video", VIDEO_EXTENSIONS)

    print("Select your audio file...")
    audio = pick_file("Select audio file", "audio", AUDIO_EXTENSIONS)

    name = input("\nWhat should the merged file be named? (without extension, default 'output'): ").strip()
    if name == "":
        name = "output"

    name = os.path.splitext(name)[0]
    output = f"{name}.mp4"

    try:
        merge(video, audio, output)
    except Exception as e:
        print(f"\n❌ Error: {e}")