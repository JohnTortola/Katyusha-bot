import os
import time


def clean_audios(AUDIO_FOLDER, current_queues, MAX_FILES=30, DELETE_AMOUNT=5):
    """
    Clean up the audio folder by deleting the oldest files when the number exceeds MAX_FILES.

    Parameters:
        AUDIO_FOLDER (str): Path to the folder containing the audio files.
        current_queue (list): List of paths of currently queued audio files to avoid deleting.
        MAX_FILES (int): Maximum number of files to keep in the folder.
        DELETE_AMOUNT (int): Number of files to delete when the max is exceeded.
    """
    
    # Get all .mp3 files with their access times
    files = [
        (os.path.join(AUDIO_FOLDER, f), os.path.getatime(os.path.join(AUDIO_FOLDER, f)))
        for f in os.listdir(AUDIO_FOLDER)
        if f.endswith(".mp3")
    ]
    
    # Sort files by last access time (oldest first)
    files.sort(key=lambda x: x[1])

    # Check if the number of files exceeds MAX_FILES
    if len(files) > MAX_FILES:
        # Files to remove is the fixed amount (DELETE_AMOUNT)
        files_to_remove = []
        
        for file_path, _ in files[:DELETE_AMOUNT]:  # Check the oldest files first
            # If the file is not in the current queue, add it to the files to remove
            if file_path not in current_queues:
                files_to_remove.append(file_path)
        
        # Delete the files that need to be removed
        for file_path in files_to_remove:
            print(f"Deleting {file_path} (last accessed {time.ctime(os.path.getatime(file_path))})")
            os.remove(file_path)
            print("\nFolder has been cleaned")
