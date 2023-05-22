def fill_missing_times(word_segments, videoDuration):
    for idx, segment in enumerate(word_segments):
        if 'start' not in segment:
            if idx == 0:  # If it's the first segment
                segment['start'] = 0.0
            else:  # Grab end time from the previous segment
                for i in range(idx-1, -1, -1):
                    if 'end' in word_segments[i]:
                        segment['start'] = word_segments[i]['end']
                        break

        if 'end' not in segment:
            if idx == len(word_segments) - 1:  # If it's the last segment
                segment['end'] = videoDuration
            else:  # Grab start time from the next segment
                for i in range(idx+1, len(word_segments)):
                    if 'start' in word_segments[i]:
                        segment['end'] = word_segments[i]['start']
                        break
    return word_segments
