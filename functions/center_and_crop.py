from moviepy.editor import *

def center_and_crop(video):
    # Check aspect ratio of input video
    orig_aspect_ratio = video.w / video.h

    # Set target aspect ratio for 9:16
    target_aspect_ratio = 9 / 16

    if orig_aspect_ratio > target_aspect_ratio:
        # Original video is wider than target, so crop horizontally
        target_width = video.h * target_aspect_ratio
        x1 = (video.w - target_width) / 2
        x2 = x1 + target_width
        y1 = 0
        y2 = video.h
    else:
        # Original video is taller than target, so crop vertically
        target_height = video.w / target_aspect_ratio
        y1 = (video.h - target_height) / 2
        y2 = y1 + target_height
        x1 = 0
        x2 = video.w

    # Crop the video to the target dimensions
    video = video.crop(x1=x1, y1=y1, x2=x2, y2=y2)

    # Resize video to 1080p (1920x1080) while preserving aspect ratio
    video = video.resize(height=1080)

    return video
