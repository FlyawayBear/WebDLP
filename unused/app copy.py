from flask import Flask, render_template, request, send_file
import subprocess
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    quality = request.form.get('quality')
    is_playlist = request.form.get('is_playlist')
    format = request.form.get('format')

    command = ['yt-dlp', url, '-o', 'bb/%(title)s.%(ext)s']

    if quality:
        command.extend(['-f', quality])

    if is_playlist:
        command.append('--yes-playlist')

    if format:
        command.extend(['-f', 'best', '--recode-video', format])

    try:
        subprocess.Popen(command)
        print("Video download started")
        message = "Video download started"

        # Wait for 20 seconds for the file to download
        time.sleep(20)

        # Get the filename of the downloaded file
        filename = subprocess.check_output(['ls', 'bb']).decode().strip()

        # Send the file for download
        return send_file(f'bb/{filename}', as_attachment=True)

    except Exception as e:
        print("Error downloading video:", e)
        message = "Error downloading video"

    return render_template('index.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
