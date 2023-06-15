import os, time

def delete_uploads_folder():
    print('Deleting old files from uploads folder')
    folder_path = 'uploads'
    time_threshold = time.time() - 2*60*60  # Files older than 2 hours

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # Check the time of the last access and remove old files
        if os.path.getmtime(file_path) < time_threshold:
            os.remove(file_path)
