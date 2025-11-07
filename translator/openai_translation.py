import os
import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY
openai.api_base = settings.OPENAI_API_BASE
def translate(text, source_lang, target_lang):
    response = openai.Completion.create(
        engine="TheBloke/Llama-2-7b-chat-fp16",
        prompt=f"Translate from {source_lang} to {target_lang}:\n{text}",
        temperature=0.7,
        max_tokens=1024,
        n = 1,
        stop=None,
        )
    return response.choices[0].text.strip()
