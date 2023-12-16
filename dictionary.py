import json
import nltk
from nltk.corpus import words

nltk.download('words')

def save_words_to_json(filename):
    word_list = words.words()

    with open(filename, 'w') as file:
        json.dump(word_list, file, indent=4)

    print(f"Saved {len(word_list)} words to {filename}")

save_words_to_json('dictionary.json');