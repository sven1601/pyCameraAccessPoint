import time
from datetime import datetime
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FfmpegOutput
import libcamera
import os
from configparser import ConfigParser

# Paths
cameraSettingsFile = '/home/cam/PythonVenv/Cam/settings.ini'

# Globals
config = ConfigParser()
config.read(cameraSettingsFile)
flipH = config.getint('main', 'flipH')
flipV = config.getint('main', 'flipV')

# Video recording
def record_video(filename, duration=60):
    global flipH
    global flipV
    
    camera = Picamera2()
    config = camera.create_video_configuration(main={"size": (1280, 720)})

    if flipH == 0 and flipV == 0:
        config["transform"] = libcamera.Transform(hflip=False, vflip=False)
    elif flipH == 1 and flipV == 0:
        config["transform"] = libcamera.Transform(hflip=True, vflip=False)
    elif flipH == 0 and flipV == 1:
        config["transform"] = libcamera.Transform(hflip=False, vflip=True)
    elif flipH == 1 and flipV == 1:
        config["transform"] = libcamera.Transform(hflip=True, vflip=True)
    camera.configure(config)

    # Limit framerate and bitrate for better CPU load on Raspi Zero
    camera.controls.FrameRate = 20    
    encoder = H264Encoder(bitrate=2500000)
    output = FfmpegOutput(filename)
    camera.start_recording(encoder, output)

    time.sleep(duration)
    camera.stop_recording()
    camera.close()

# File management (to limit the amount of video files, called loop recording)
def manage_videos(directory, max_videos=3000):
    files = sorted(os.listdir(directory), key=lambda x: os.path.getctime(os.path.join(directory, x)))
    # Delete the oldest file, as long as the limit is exceeded
    while len(files) > max_videos:
        os.remove(os.path.join(directory, files[0]))
        files = sorted(os.listdir(directory), key=lambda x: os.path.getctime(os.path.join(directory, x)))

def main():
    video_dir = os.path.expanduser("~/video_files")
    video_duration = 60  # Video duration

    # Create output folder if it doesn't exist
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)

    # Loop for recording
    while True:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = os.path.join(video_dir, f"video_{timestamp}_{video_duration}sec_temp.mp4")
        record_video(video_filename, video_duration)
        # Manage the files after every record
        manage_videos(video_dir)
        # Create the final filename, to mark it as finsihed
        new_filename = video_filename.replace('_temp.mp4', '.mp4')
        os.rename(video_filename, new_filename)

if __name__ == "__main__":
    main()
