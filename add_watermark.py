from moviepy.editor import ImageClip, CompositeVideoClip

def add_watermark(video, clip_info):

    # Choose the watermark image based on conditions
    if clip_info.get('watermarkToggle') == 'on':
        watermark_path = "watermarks/PCB_1.png"
    elif clip_info.get('subscription') == 'none':
        watermark_path = "watermarks/PCB_fv_1.png"
    else:
        video = CompositeVideoClip([video])
        return video

    # Add the watermark image overlay
    watermark = ImageClip(watermark_path)
    watermark = watermark.set_opacity(0.9).resize(height=190)
    watermark = watermark.set_pos(lambda t: ('center', video.size[1] * 0.75 - watermark.size[1] / 2))
    video = CompositeVideoClip([video, watermark.set_duration(video.duration)])

    return video
