from googletrans import Translator
from .openai_client import openai

translator = Translator()


def translate(text, source_lang, target_lang):
    # First, translate the text to English using Google Translate
    english_text = translator.translate(text, dest='en').text

    # Then, use OpenAI GPT to translate the English text to the target language
    prompt = f"translate '{english_text}' from {source_lang} to {target_lang}:"
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return response.choices[0].text.strip()
