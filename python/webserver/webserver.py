from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import subprocess
import os
import signal
import datetime

app = Flask(__name__)

# Globale Variablen, um die Subprozesse zu speichern
process1 = None
process2 = None

# Pfad zum Ordner mit den aufzulistenden Dateien
files_dir = '/home/cam/video_files/'

@app.route("/", methods=["GET", "POST"])
def index():
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if request.method == "POST":
        try:
            # Zeit vom Client empfangen (im Format 'YYYY-MM-DD HH:MM:SS')
            new_time = request.form["new_time"] 
            # Befehl zum Setzen der Systemzeit ausführen
            subprocess.run(["sudo", "date", "-s", new_time])  
            return "Time is set!"
        except Exception as e:
            return f"Error during time setting: {e}"
    return render_template("index.html", current_time=current_time)

@app.route('/start_camScript')
def start_script1():
    global process1
    if process1 is None or process1.poll() is not None:  # Startet nur, wenn es nicht bereits läuft
        with open("/home/cam/PythonVenv/Cam/output.txt", "w") as outfile, open("/home/cam/PythonVenv/Cam/error.txt", "w") as errfile:
            process1 = subprocess.Popen(['/home/cam/PythonVenv/Cam/bin/python', '/home/cam/PythonVenv/Cam/camera.py'], stdout=outfile, stderr=errfile)
            return 'camera.py is running'
    else:
        return 'camera.py is already running'

@app.route('/stop_camScript')
def stop_script1():
    global process1
    if process1 is not None and process1.poll() is None:
        os.kill(process1.pid, signal.SIGTERM)  # Sendet SIGTERM zum Beenden
        process1 = None
        return 'camera.py is stopped'
    else:
        return 'camera.py is not running'

@app.route('/list_files')
def list_files():
    file_list = os.listdir(files_dir)
    file_list.sort(reverse = True)
    return render_template('files.html', files=file_list)

@app.route('/files/<filename>')
def serve_file(filename):
    return send_from_directory(files_dir, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
