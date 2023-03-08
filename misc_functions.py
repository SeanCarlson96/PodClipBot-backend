import cv2
from moviepy.editor import *

# code blocks assume the working variable for the video file is called video

# Add subtitles
# txt_clip = TextClip("Hello, world!", fontsize=50, color='white')
# txt_clip = txt_clip.set_pos('bottom').set_duration(video.duration)
# video = CompositeVideoClip([video, txt_clip])

# Add background music. This works but it replaces the video audio. I just
# need the music quiet in the background
# audio_clip = AudioFileClip("impressionist.mp3")
# audio_clip = audio_clip.set_duration(video.duration)
# video = video.set_audio(audio_clip)

# Add watermark image overlay
# watermark = ImageClip("SClogoWatermark.png")
# watermark = watermark.set_opacity(0.9).resize(height=50)
# watermark = watermark.set_pos(('right', 'bottom'))
# video = CompositeVideoClip([video, watermark])