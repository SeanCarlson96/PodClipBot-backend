import magic


def safe_watermark_file(file, max_file_size_MB):
    ALLOWED_MIME_TYPES = [
        'image/jpeg',  # JPEG
        'image/png',   # PNG
        'image/gif',   # GIF
        'image/bmp',   # BMP
        'image/svg+xml',  # SVG
        'image/tiff',  # TIFF
        'image/webp',  # WebP
        'image/heif',  # HEIF
        'image/x-icon',  # ICO
    ]
    
    # Check file size
    file_size_MB = len(file.read()) / (1024 * 1024)
    if file_size_MB > max_file_size_MB:
        return False, f'File is too large. Maximum file size is {max_file_size_MB}MB.'

    # Check file type
    # mime_type = magic.from_buffer(file.read(1024), mime=True)
    # if mime_type not in ALLOWED_MIME_TYPES:
    #     return False, f'Invalid file type. Allowed file types are: JPEG, PNG, GIF, BMP, SVG, TIFF, WebP, HEIF, ICO.'

    file.seek(0)
    file_data = file.read()
    file_mime_type = magic.from_buffer(file_data, mime=True)
    file.seek(0) # seek back to start after reading

    if file_mime_type not in ALLOWED_MIME_TYPES:
        return False, f'File type not allowed: {file_mime_type}'


    return True, 'File is safe.'
