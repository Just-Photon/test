import json
import time
from googletrans import Translator
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

def format_time(seconds):
    # Converts time in seconds to a more readable format (days, hours, minutes, seconds).
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

def translate_and_save(word, languages, translator, output_file, lock):
    translations = {}
    for lang in languages:
        try:
            translated = translator.translate(word, dest=lang).text
            translations[lang] = translated
        except Exception as e:
            translations[lang] = ""
    
    with lock:
        with open(output_file, 'r+', encoding='utf-8') as file:
            existing_translations = json.load(file)
            existing_translations[word] = translations
            file.seek(0)
            json.dump(existing_translations, file, indent=4, ensure_ascii=False)
            file.truncate()

def translate_words(input_file, output_file, languages):
    translator = Translator()
    lock = Lock()

    # Initialize an empty JSON file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump({}, file, indent=4, ensure_ascii=False)

    with open(input_file, 'r', encoding='utf-8') as file:
        try:
            words = json.load(file)
        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
            return

    total_words = len(words)
    processed_count = 0
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(translate_and_save, word, languages, translator, output_file, lock) for word in words]

        for future in as_completed(futures):
            processed_count += 1
            elapsed_time = time.time() - start_time
            avg_time_per_word = elapsed_time / processed_count if processed_count else 0
            estimated_total_time = avg_time_per_word * total_words
            remaining_time = estimated_total_time - elapsed_time
            formatted_time = format_time(remaining_time)
            print(f"Processed {processed_count}/{total_words} words. Estimated time remaining: {formatted_time}", end='\r')

    print(f"\nTranslations saved to {output_file}")

# Usage
languages_to_translate = ['no', 'en', 'zh-CN', 'ja']
translate_words('dictionary.json', 'translation.json', languages_to_translate)
