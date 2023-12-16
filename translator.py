import json
from googletrans import Translator, LANGUAGES

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

    for word in words:
        # Skip if the word is less than one character
        if len(word) < 2:
            continue

        if word not in translations:
            translations[word] = {}

        for lang in languages:
            # Skip if the word has already been translated in this language
            if lang in translations[word]:
                continue

            # Translate each word
            try:
                translated = translator.translate(word, dest=lang).text
                translations[word][lang] = translated
            except Exception as e:
                print(f"Error translating {word} to {lang}: {e}")
                translations[word][lang] = ""

        processed_count += 1
        print(f"Processed {processed_count}/{total_words} words", end='\r')

    # Save translations to a JSON file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(translations, file, indent=4, ensure_ascii=False)

    print(f"\nTranslations saved to {output_file}")

# Usage
languages_to_translate = ['no', 'en', 'zh-CN', 'ja']  # Add more language codes as needed
translate_words('dictionary.json', 'translation.json', languages_to_translate)