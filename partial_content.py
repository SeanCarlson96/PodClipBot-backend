import os
from flask import Flask, Response, request
import re


def partial_content_handler(file_path, range_header):
    size = os.path.getsize(file_path)
    byte1, byte2 = 0, None

    if range_header:
        match = re.match(r'bytes=(\d+)-(\d+)?', range_header)
        if match:
            byte1, byte2 = match.groups()
            byte1 = int(byte1)

            if byte2:
                byte2 = int(byte2)

    length = size - byte1
    if byte2 is not None:
        length = byte2 - byte1 + 1

    with open(file_path, 'rb') as f:
        f.seek(byte1)
        bytes = f.read(length)

    response = Response(bytes, 206, mimetype='video/mp4',
                        content_type='video/mp4', direct_passthrough=True)
    response.headers.add('Content-Range', f'bytes {byte1}-{byte1 + length - 1}/{size}')
    response.headers.add('Accept-Ranges', 'bytes')

    return response
