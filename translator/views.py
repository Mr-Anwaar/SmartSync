from django.shortcuts import render
from .openai_translation import *


def translation(request):
    if request.method == 'POST':
        text = request.POST['text']
        source_lang = request.POST['source_lang']
        target_lang = request.POST['target_lang']
        translated_text = translate(text, source_lang, target_lang)
    else:
        text = ''
        source_lang = 'en'
        target_lang = 'ur'
        translated_text = ''

    return render(request, 'translation/translation.html', {
        'text': text,
        'source_lang': source_lang,
        'target_lang': target_lang,
        'translated_text': translated_text,
    })
