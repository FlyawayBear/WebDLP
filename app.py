import uuid
import shutil
import subprocess
import os
import zipfile
import time
from flask import Flask, render_template, request, send_file

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

            if format:
                command.extend(['-f', 'best', '--recode-video', format])

            subprocess.run(command, check=True)
            print("Playlist download complete")

            # Create a zip file containing the downloaded files
            zip_filename = f'{request_id}.zip'
            with zipfile.ZipFile(zip_filename, 'w') as zip_file:
                for filename in os.listdir(temp_dir):
                    zip_file.write(os.path.join(temp_dir, filename), filename)

            # Send the zip file for download
            return send_file(zip_filename, as_attachment=True)

        else:
            # Create a temporary directory to store the downloaded file
            video_dir = f'video_{request_id}'
            os.makedirs(video_dir, exist_ok=True)

            # Download a single video
            command = ['yt-dlp', url, '--no-playlist','-o', f'{video_dir}/%(title)s.%(ext)s']

            if quality:
                command.extend(['-f', quality])

            if format:
                command.extend(['-f', 'best', '--recode-video', format])

            subprocess.Popen(command)
            print("Video download started")
            message = "Video download started"

            # Wait for 20 seconds for the file to download
            time.sleep(20)

            # Get the filename of the downloaded file
            filename = subprocess.check_output(['ls', video_dir]).decode().strip()

            # Send the file for download
            return send_file(f'{video_dir}/{filename}', as_attachment=True)

    except Exception as e:
        print("Error downloading video:", e)
        message = "Error downloading video"
        return render_template('index.html', message=message)

    finally:
        # Clean up the temporary directories and files
        if is_playlist:
            shutil.rmtree(temp_dir, ignore_errors=True)
            os.remove(zip_filename)
        else:
            shutil.rmtree(video_dir, ignore_errors=True)

if __name__ == '__main__':
    app.run(debug=True)
