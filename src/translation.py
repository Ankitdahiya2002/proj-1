from googletrans import Translator

translator = Translator()

def to_english(text, src_lang="hi"):
    return translator.translate(text, src=src_lang, dest="en").text

def to_hindi(text, src_lang="en"):
    return translator.translate(text, src=src_lang, dest="hi").text
