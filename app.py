import uuid
import shutil
import subprocess
import os
import zipfile
import time
from flask import Flask, render_template, request, send_file
import ffmpeg

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

            # Convert the videos using FFmpeg
            for filename in os.listdir(temp_dir):
                input_file = f'{temp_dir}/{filename}'
                output_file = f'{temp_dir}/converted.{format}'
                ffmpeg.input(input_file).output(output_file).run()

            # Create a zip file containing the converted files
            zip_filename = f'{request_id}.zip'
            with zipfile.ZipFile(zip_filename, 'w') as zip_file:
                for filename in os.listdir(temp_dir):
                    if filename.endswith(f'.{format}'):
                        zip_file.write(os.path.join(temp_dir, filename), filename)

            # Send the zip file for download
            return send_file(zip_filename, as_attachment=True)

        else:
            # Create a temporary directory to store the downloaded file
            video_dir = f'webdlp_{request_id}'
            os.makedirs(video_dir, exist_ok=True)

            # Download a single video
            command = ['yt-dlp', url, '--no-playlist']

            if quality:
                command.extend(['-f', quality])

            subprocess.run(command, check=True)
            print("Video download complete")

            # Convert the video using FFmpeg
            input_file = f'{video_dir}/{os.listdir(video_dir)[0]}'
            output_file = f'{video_dir}/converted.{format}'
            ffmpeg.input(input_file).output(output_file).run()

            # Send the file for download
            return send_file(output_file, as_attachment=True)

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
