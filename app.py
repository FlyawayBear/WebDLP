import uuid
import shutil
import subprocess
import os
import zipfile
import time
from flask import Flask, render_template, request, send_file, redirect, url_for

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

    # Generate a unique identifier for the request
    request_id = str(uuid.uuid4())

    try:
        if is_playlist:
            # Create a temporary directory to store the downloaded files
            temp_dir = f'temp_{request_id}'
            os.makedirs(temp_dir, exist_ok=True)

            # Download the playlist
            command = ['yt-dlp', url, '-o', f'{temp_dir}/%(playlist_index)s-%(title)s.%(ext)s']

            if quality:
                command.extend(['-f', quality])

            subprocess.run(command, check=True)
            print("Playlist download complete")

            # Convert the videos to the specified format using ffmpeg
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                output_filename = f"{os.path.splitext(file_path)[0]}.{format}"
                subprocess.run(['ffmpeg', '-i', file_path, output_filename], check=True)
                os.remove(file_path)

            # Create a zip file containing the converted files
            zip_filename = f'{request_id}.zip'
            with zipfile.ZipFile(zip_filename, 'w') as zip_file:
                for filename in os.listdir(temp_dir):
                    converted_filename = f"{os.path.splitext(filename)[0]}.{format}"
                    zip_file.write(os.path.join(temp_dir, converted_filename), converted_filename)

            # Send the zip file for download
            return send_file(zip_filename, as_attachment=True)

        else:
            # Create a temporary directory to store the downloaded file
            video_dir = f'temp_{request_id}'
            os.makedirs(video_dir, exist_ok=True)

            # Download a single video
            command = ['yt-dlp', url, '--no-playlist','-o', f'{video_dir}/%(title)s.%(ext)s']

            if quality:
                command.extend(['-f', quality])

            subprocess.Popen(command)
            print("Video download started")
            
            # Redirect to the download started page
            return redirect(url_for('download_started'))

    except Exception as e:
        print("Error downloading video:", e)
        message = "Error downloading video"
        return render_template('index.html', message=message)

@app.route('/download-started')
def download_started():
    message = "Your download has started."
    return render_template('download_started.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
