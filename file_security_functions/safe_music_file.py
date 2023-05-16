import magic


def safe_music_file(file, max_file_size_MB):
    ALLOWED_MIME_TYPES = [
        'audio/mpeg',  # MP3
        'audio/wav',   # WAV
        'audio/aac',   # AAC
        'audio/flac',  # FLAC
        'audio/mp4',   # M4A
        'audio/ogg',   # OGG, OPUS
        'audio/x-aiff', # AIFF
        'audio/vnd.wave',  # WMA
    ]
    
    # Check file size
    file_size_MB = len(file.read()) / (1024 * 1024)
    if file_size_MB > max_file_size_MB:
        return False, f'File is too large. Maximum file size is {max_file_size_MB}MB.'

    # file.seek(0)
    # # Check file type
    # mime_type = magic.from_buffer(file.read(1024), mime=True)
    # # mime = magic.Magic(mime=True)
    # # mime_type = mime.from_file(file) # 'application/pdf'

    # print(mime_type)
    # if mime_type not in ALLOWED_MIME_TYPES:
    #     return False, f'Invalid file type. Allowed file types are: MP3, WAV, AAC, FLAC, M4A, OGG, OPUS, ALAC, AIFF, WMA.'

    file.seek(0)
    file_data = file.read()
    file_mime_type = magic.from_buffer(file_data, mime=True)
    file.seek(0) # seek back to start after reading
    print(file_mime_type)

    if file_mime_type not in ALLOWED_MIME_TYPES:
        return False, f'File type not allowed: {file_mime_type}'




    return True, 'File is safe.'
