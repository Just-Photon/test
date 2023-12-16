import json
import time
from googletrans import Translator, LANGUAGES
from concurrent.futures import ThreadPoolExecutor, as_completed

def format_time(seconds):
    """Converts time in seconds to a more readable format (days, hours, minutes, seconds)."""
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

def translate_word(word, languages, translator):
    translations = {}
    for lang in languages:
        try:
            translated = translator.translate(word, dest=lang).text
            translations[lang] = translated
        except Exception as e:
            print(f"Error translating {word} to {lang}: {e}")
            translations[lang] = ""
    return word, translations

def translate_words(input_file, output_file, languages):
    translator = Translator()

    # Load words from JSON file
    with open(input_file, 'r', encoding='utf-8') as file:
        try:
            words = json.load(file)
        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
            return

    # Initialize translations as an empty dictionary
    translations = {}

    # Try to load existing translations if available
    try:
        with open(output_file, 'r', encoding='utf-8') as file:
            existing_translations = json.load(file)
            if isinstance(existing_translations, dict):
                translations.update(existing_translations)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    total_words = len(words)
    processed_count = 0
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_word = {executor.submit(translate_word, word, languages, translator): word for word in words if word not in translations}

        for future in as_completed(future_to_word):
            word = future_to_word[future]
            try:
                word, word_translations = future.result()
                if word not in translations:
                    translations[word] = {}
                translations[word].update(word_translations)
                processed_count += 1
            except Exception as e:
                print(f"Error translating {word}: {e}")

            elapsed_time = time.time() - start_time
            avg_time_per_word = elapsed_time / processed_count if processed_count else 0
            estimated_total_time = avg_time_per_word * total_words
            remaining_time = estimated_total_time - elapsed_time

            formatted_time = format_time(remaining_time)
            print(f"Processed {processed_count}/{total_words} words. Estimated time remaining: {formatted_time}", end='\r')

    # Save translations to a JSON file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(translations, file, indent=4, ensure_ascii=False)

    print(f"\nTranslations saved to {output_file}")

# Usage
languages_to_translate = ['no', 'en', 'zh-CN', 'ja']  # Add more language codes as needed
translate_words('dictionary.json', 'translation.json', languages_to_translate)
