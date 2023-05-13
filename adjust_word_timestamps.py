# def adjust_word_timestamps(result_aligned):
#     for word_segment in result_aligned['word_segments']:
#         word = word_segment['word']
#         for segment in result_aligned['segments']:
#             chars = [char for char in segment['chars'] if 'char' in char and char['char'] in word]
#             if chars:
#                 word_segment['start'] = chars[0]['start']
#                 word_segment['end'] = chars[-1]['end']

#     return result_aligned

def adjust_word_timestamps(result_aligned):
    new_word_segments = []
    current_word = ''
    start_time = None
    end_time = None

    for segment in result_aligned['segments']:
        for char in segment['chars']:
            # If char is a space, end current word and start a new one
            if char.get('char') == ' ':
                if current_word:
                    new_word_segments.append({
                        'word': current_word,
                        'start': start_time,
                        'end': end_time,
                        'score': 0.0,  # Not sure how you want to calculate score
                    })
                current_word = ''
                start_time = None
            else:
                # If this is the first char of the word, set the start_time
                if not current_word:
                    start_time = char.get('start')
                # Update current_word and end_time
                current_word += char.get('char', '')
                end_time = char.get('end')

        # Check if there is an unfinished word at the end of the segment
        if current_word:
            new_word_segments.append({
                'word': current_word,
                'start': start_time,
                'end': end_time,
                'score': 0.0,  # Not sure how you want to calculate score
            })
            
    result_aligned['word_segments'] = new_word_segments

    return result_aligned

