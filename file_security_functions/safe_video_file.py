import os
import magic

def safe_video_file(file, max_file_size_mb):
    """
    Check if the uploaded file is safe

    :param file: the file to check
    :param max_file_size_mb: maximum allowed file size in megabytes
    :return: True if the file is safe, False otherwise
    """
    max_file_size_bytes = max_file_size_mb * 1024 * 1024

    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # reset file pointer to start of file
    if file_size > max_file_size_bytes:
        return False, "File size is too large"

    # Check file type
    mime = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)  # reset file pointer to start of file
    if mime not in ['video/mp4', 'video/webm', 'video/ogg', 'video/quicktime', 'video/x-msvideo', 'video/x-flv', 'video/x-matroska', 'video/x-ms-wmv', 'video/mpeg', 'video/3gpp', 'video/x-m4v']:
        return False, "Invalid file type"

    # Check file name to prevent directory traversal attacks
    if '/' in file.filename or '\\' in file.filename or ':' in file.filename:
        return False, "Invalid file name"

    return True, "File is safe"
