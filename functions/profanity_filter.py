# profanity_filter.py

def censor(word):
    return word[0] + '*' * (len(word) - 2) + word[-1] if len(word) > 2 else word

def check_profanity(word):
    # List of bad words to censor in subtitles
    swear_words = ['fuck', 'fucking', 'shit', 'shitting', 'ass', 'dumbass', 'bitch', 'nigger', 'nigga', 'cunt', 'slut', 'whore']
    if word.lower() in swear_words:
        return censor(word)
    return word
