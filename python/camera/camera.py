import time
from datetime import datetime
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FfmpegOutput
import os

# Funktion zur Videoaufnahme
def record_video(filename, duration=60):
    camera = Picamera2()
    config = camera.create_video_configuration(main={"size": (1280, 720)})
    camera.configure(config)

    # Verwende FfmpegOutput mit libx264-Encoder
    encoder = H264Encoder(bitrate=5000000)
    output = FfmpegOutput(filename)
    camera.start_recording(encoder, output)

    time.sleep(duration)
    camera.stop_recording()
    camera.close()

# Funktion zum Verwalten der Videos im Ordner (unverändert)
def manage_videos(directory, max_videos=3000):
    files = sorted(os.listdir(directory), key=lambda x: os.path.getctime(os.path.join(directory, x)))
    while len(files) > max_videos:
        os.remove(os.path.join(directory, files[0]))
        files = sorted(os.listdir(directory), key=lambda x: os.path.getctime(os.path.join(directory, x)))

def main():
    video_dir = os.path.expanduser("~/video_files")  # Benutze os.path.expanduser
    video_duration = 5  # Sekunden

    if not os.path.exists(video_dir):
        os.makedirs(video_dir)

    while True:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = os.path.join(video_dir, f"video_{timestamp}.mp4")  # Ändere die Dateierweiterung zu .mp4

        # Aufnahme des Videos
        record_video(video_filename, video_duration)

        print(video_filename)

        # Verwalten der Videos im Ordner
        #manage_videos(video_dir)

if __name__ == "__main__":
    main()
