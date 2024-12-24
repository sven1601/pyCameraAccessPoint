from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import subprocess
from subprocess import call
import os
import signal
import datetime
from configparser import ConfigParser

app = Flask(__name__)

# Globale Variablen, um die Subprozesse zu speichern
cameraProcess = None
pictureProcess = None

config = ConfigParser()

# Pfad zum Ordner mit den aufzulistenden Dateien
files_dir = '/home/cam/video_files/'
cameraSettingsFile = '/home/cam/PythonVenv/Cam/settings.ini'
testPicture = '/home/cam/PythonVenv/Webserver/static/testPic.jpg'

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Zeit vom Client empfangen (im Format 'YYYY-MM-DD HH:MM:SS')
            new_time = request.form["time"] 
            # Befehl zum Setzen der Systemzeit ausführen
            subprocess.run(["sudo", "date", "-s", new_time])  
            return "Time is set!"
        except Exception as e:
            return f"Error during time setting: {e}"
    return render_template("index.html")

@app.route('/start_camScript')
def start_script1():
    global cameraProcess
    if cameraProcess is None or cameraProcess.poll() is not None:  # Startet nur, wenn es nicht bereits läuft
        with open("/home/cam/PythonVenv/Cam/output.txt", "w") as outfile, open("/home/cam/PythonVenv/Cam/error.txt", "w") as errfile:
            cameraProcess = subprocess.Popen(['/home/cam/PythonVenv/Cam/bin/python', '/home/cam/PythonVenv/Cam/camera.py'], stdout=outfile, stderr=errfile)
            return f'camera.py is running ---> PID {cameraProcess.pid}'
    else:
        return 'camera.py is already running'

@app.route('/stop_camScript')
def stop_script1():
    global cameraProcess
    if cameraProcess is not None and cameraProcess.poll() is None:
        oldPid = cameraProcess.pid
        os.kill(cameraProcess.pid, signal.SIGTERM)  # Sendet SIGTERM zum Beenden
        cameraProcess = None
        return f'camera.py is stopped ---> PID {oldPid}'
    else:
        return 'camera.py is not running'

@app.route('/list_files')
def list_files():
    file_list = os.listdir(files_dir)
    file_list.sort(reverse = True)
    fileCount = len(file_list)
    return render_template('files.html', files=file_list, fileNum=fileCount)

@app.route('/files/<filename>')
def serve_file(filename):
    return send_from_directory(files_dir, filename)

@app.route('/reboot')
def reboot():
    call("sudo reboot", shell=True)
    return 'Reboot initiated'

@app.route('/shutdown')
def shutdown():
    call("sudo shutdown -h now", shell=True)
    return 'Shutdown initiated'

@app.route('/flipH')
def flipH():
    config.read(cameraSettingsFile)
    config.set('main', 'flipH', '1')
    with open(cameraSettingsFile, 'w') as f:
        config.write(f)
    return get_picture()

@app.route('/flipH_not')
def flipH_not():
    config.read(cameraSettingsFile)
    config.set('main', 'flipH', '0')
    with open(cameraSettingsFile, 'w') as f:
        config.write(f)
    return get_picture()

@app.route('/flipV')
def flipV():
    config.read(cameraSettingsFile)
    config.set('main', 'flipV', '1')
    with open(cameraSettingsFile, 'w') as f:
        config.write(f)
    return get_picture()

@app.route('/flipV_not')
def flipV_not():
    config.read(cameraSettingsFile)
    config.set('main', 'flipV', '0')
    with open(cameraSettingsFile, 'w') as f:
        config.write(f)
    return get_picture()

@app.route('/flip_reset')
def flip_reset():
    config.read(cameraSettingsFile)
    config.set('main', 'flipH', '0')
    config.set('main', 'flipV', '0')
    with open(cameraSettingsFile, 'w') as f:
        config.write(f)
    return get_picture()

@app.route('/get_picture')
def get_picture():
    call(f'rm {testPicture}', shell=True)

    config.read(cameraSettingsFile)
    flipH = config.getint('main', 'flipH')
    flipV = config.getint('main', 'flipV')
    if flipH == 0 and flipV == 0:
        pictureProcess = subprocess.Popen(['rpicam-still', '-o', testPicture, '--width', '640', '--height', '480'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif flipH == 1 and flipV == 0:
        pictureProcess = subprocess.Popen(['rpicam-still', '-o', testPicture, '--width', '640', '--height', '480', '--hflip'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif flipH == 0 and flipV == 1:
        pictureProcess = subprocess.Popen(['rpicam-still', '-o', testPicture, '--width', '640', '--height', '480', '--vflip'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif flipH == 1 and flipV == 1:
        pictureProcess = subprocess.Popen(['rpicam-still', '-o', testPicture, '--width', '640', '--height', '480', '--hflip', '--vflip'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pictureProcess.wait()
    (stdout, stderr) = pictureProcess.communicate()

    if pictureProcess.returncode != 0:
        return stderr
    else:
        return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
