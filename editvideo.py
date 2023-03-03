from moviepy.editor import *

# Load video clip
clip = VideoFileClip("input_video.mp4")

# Trim clip
clip = clip.subclip(10, 30) # trim clip from 10 to 30 seconds

# Crop clip
clip = crop(clip, width=720, height=480, x1=0, y1=80) # crop to (720, 480) starting at (0, 80)

# Center on a subject
centered_clip = clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=480, height=480)

# Add background music
bg_music = AudioFileClip("bg_music.mp3")
clip_with_music = centered_clip.set_audio(bg_music)

# Add subtitles
subtitles = SubtitlesClip("subtitles.srt")
clip_with_subtitles = CompositeVideoClip([clip_with_music, subtitles.set_pos(('center','bottom'))])

# Add watermark
watermark = ImageClip("watermark.png")
watermark = watermark.set_duration(clip.duration).resize(height=50)
final_clip = CompositeVideoClip([clip_with_subtitles, watermark.set_pos((10, 10))])

# Export final clip
final_clip.write_videofile("output_video.mp4", fps=24)
