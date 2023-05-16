from moviepy.editor import *

def center_and_crop(video):
    # Crop the video to a 9:16 aspect ratio and 1920x1080 resolution
    target_width = 1080*9//16
    x1 = (video.w // 2) - (target_width // 2)
    x2 = x1 + target_width
    y1 = 0
    y2 = 1080
    video = video.crop(x1=x1, y1=y1, x2=x2, y2=y2)
    video = video.resize(width=1920)
    return video
