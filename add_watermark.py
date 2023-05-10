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
    
    position_horizontal = clip_info.get('watermarkPositionHorizontal')
    position_vertical = ((100 - int(clip_info.get('watermarkPositionVertical', '45'))) / 100)
    custom_upload = clip_info.get('watermark-file', None)
    height = clip_info.get('watermarkSize')
    opacity = int(clip_info.get('watermarkOpacity')) / 100
    duration = clip_info.get('watermarkDuration')

    if custom_upload:
        watermark_path = custom_upload

    # Add the watermark image overlay
    watermark = ImageClip(watermark_path)
    watermark = watermark.set_opacity(opacity).resize(height=height)
    # watermark = watermark.set_pos(lambda t: ('center', video.size[1] * 0.75 - watermark.size[1] / 2))
    watermark = watermark.set_pos(position_horizontal, position_vertical)
    video = CompositeVideoClip([video, watermark.set_duration(video.duration * (duration / 100.0))])

    return video
