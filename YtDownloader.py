import yt_dlp
import os
import re

# Remove characters that are not safe in filenames
def sanitize_filename(filename):
    return re.sub(r'[^\w\s.-]', '', filename)

def download_audio(url, output_path, ffmpeg_path, ffprobe_path):

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    try:
        # Extract info without downloading and sanitize
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl_temp:
            info = ydl_temp.extract_info(url, download=False)
            unsanitized_title = info.get("title", "untitled_audio")
            title = sanitize_filename(unsanitized_title)

            duration_seconds = info.get("duration", 0)
            if duration_seconds > 600: #10 minutes
                print("Video is too long.")
                return False, "Video duration exceeds limit", title
            
        filename = os.path.join(output_path, f"{title}.mp3")
        print(f"\n{filename}")

        if os.path.exists(filename):
            print("\nFile already exists")
            return True, filename, title

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_path, f"{title}.%(ext)s"),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': ffmpeg_path,
            'ffprobe_location': ffprobe_path,
            'quiet': False,
            'noplaylist': True,
            'postprocessor_args': ['-filter:a', 'volume=0.07']
        }


        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return True, filename, title

    except yt_dlp.utils.DownloadError as e:
        return False, f"\nError downloading the video: {str(e)}", ""

    except Exception as e:
        return False, f"\nAn unexpected error occurred: {str(e)}", ""