from moviepy.editor import ImageClip, CompositeVideoClip

def add_watermark(video):
    # Add watermark image overlay
    watermark = ImageClip("watermarks/PCB_fv_1.png")
    watermark = watermark.set_opacity(0.9).resize(height=190)
    watermark = watermark.set_pos(lambda t: ('center', video.size[1] * 0.75 - watermark.size[1] / 2))
    video = CompositeVideoClip([video, watermark.set_duration(video.duration)])
    return video