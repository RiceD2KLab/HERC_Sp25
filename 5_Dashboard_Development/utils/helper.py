# dashboard helper functions
import re
def title_case_with_spaces(text):
    if 'CISD' in text:
        words = text.split()
        words = [word.title() if word != 'CISD' else word for word in words]
        return ' '.join(words)
    if 'ISD' in text:
        words = text.split()
        words = [word.title() if word != 'ISD' else word for word in words]
        return ' '.join(words)
    if 'MSD' in text:
        words = text.split()
        words = [word.title() if word != 'MSD' else word for word in words]
        return ' '.join(words)
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', text).title()