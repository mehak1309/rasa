# Import libraries
import os
import pandas as pd
import csv
import re
import os, string, re, multiprocessing
from tqdm import tqdm
import numpy as np

language = 'mni'

all_symbols = [
    '!',      # Exclamation mark
    '"',      # Quotation mark (double)
    '#',      # Hash or pound sign
    '$',      # Dollar sign
    '%',      # Percent sign
    '&',      # Ampersand
    "'",      # Apostrophe or single quotation mark
    '(',      # Left parenthesis
    ')',      # Right parenthesis
    '*',      # Asterisk
    '+',      # Plus sign
    ',',      # Comma
    '-',      # Hyphen or minus sign
    '.',      # Period or dot
    '/',      # Slash or forward slash
    ':',      # Colon
    ';',      # Semicolon
    '<',      # Less-than sign
    '=',      # Equal sign
    '>',      # Greater-than sign
    '?',      # Question mark
    '@',      # At symbol
    '[',      # Left square bracket
    '\\',     # Backslash
    ']',      # Right square bracket
    '^',      # Caret or circumflex accent
    '_',      # Underscore
    '`',      # Grave accent or backtick
    '{',      # Left curly brace or bracket
    '|',      # Vertical bar or pipe
    '}',      # Right curly brace or bracket
    '~',      # Tilde
    '¡',      # Inverted exclamation mark
    '¢',      # Cent sign
    '£',      # Pound sterling sign
    '¤',      # Currency sign
    '¥',      # Yen sign
    '¦',      # Broken vertical bar
    '§',      # Section sign
    '¨',      # Diaeresis or umlaut
    '©',      # Copyright symbol
    '«',      # Left-pointing double angle quotation mark
    '¬',      # Logical negation symbol
    '®',      # Registered trademark symbol
    '¯',      # Macron accent
    '°',      # Degree symbol
    '±',      # Plus-minus sign
    '´',      # Acute accent
    '¶',      # Pilcrow or paragraph sign
    '·',      # Middle dot or interpunct
    '¸',      # Cedilla
    '»',      # Right-pointing double angle quotation mark
    '×',      # Multiplication sign
    '¿',      # Inverted question mark
    '—',      # Em dash
    '–',      # En dash
    '"',      # Left double quotation mark
    '"',      # Right double quotation mark
    ''',      # Left single quotation mark
    ''',      # Right single quotation mark
    '…',      # Ellipsis
    '†',      # Dagger
    '‡',      # Double dagger
    '‰',      # Per mille sign
    '′',      # Prime or minute
    '″',      # Double prime or second
    '€',      # Euro sign
    '₹',      # Indian Rupee sign
    '→',      # Right arrow
    '←',      # Left arrow
    '↑',      # Up arrow
    '↓',      # Down arrow
    '↵',      # Carriage return arrow or Enter key symbol
    '⇒',      # Rightwards double arrow
    '−',      # Minus sign
    '∩',      # Intersection
    '≡',      # Identical to
    '≤',      # Less than or equal to
    'Ⓡ',      # Registered trademark symbol in a circle
    '●',      # Black circle
    '☞',      # Hand pointing right
    '❀',      # Flower symbol
    '？',      # Fullwidth question mark (used in East Asian typography)
    '',      # Special character used in file encoding or markup
    '،',     # Arabic comma
    '؟',     # Arabic question mark
    '۔',    # Urdu full stop (called "dari" in Urdu)
    '؛',    # Arabic semicolon
    '٬',     # Arabic thousands separator
    '٫',      # Arabic decimal separator
    '٪',     # Arabic percent sign
    '٭',      # Arabic asterisk
    '۔۔۔',       # Ellipsis in Urdu
    '।',   # Danda (full stop)
    '॥',   # Double danda (full stop used to indicate the end of a paragraph)
]

symbols_silent = [".", ",", '"', "'", "?", "!", '۔', '،', '٬', '٬', '؟', '!', "؍", '।', '॥']
lang_number_dict = { 
    'as': '[\u09E6-\u09EF]+',
    'bn': '[\u09E6-\u09EF]+',
    'hi': '[\u0966-\u096F]+',
    'doi': '[\u0966-\u096F]+',
    'mr': '[\u0966-\u096F]+',
    'ta': '[\u0BE6-\u0BEF]+',
    'te': '[\u0C66-\u0C6F]+',
    'kn': '[\u0CE6-\u0CEF]+',
    'ml': '[\u0D66-\u0D6F]+',
    'or': '[\u0B66-\u0B6F]+',
    'pa': '[\u0A66-\u0A6F]+',
    'gu': '[\u0AE6-\u0AEF]+',
    'mni': '[\uABF0-\uABF9]+',
    'san': '[\u0966-\u096F]+',
    'ks': '[\u0660-\u0669]+',
    'ur': '[\u0660-\u0669]+',
    'mai': '[\u0966-\u096F]+',
    'sd': '[\u0966-\u096F]+',
    'nep': '[\u0966-\u096F]+',
    'brx': '[\u0966-\u096F]+',
    'kok': '[\u0966-\u096F]+',
    'sat': '[\u1C50-\u1C59]+',
    }

# languages = ['gu', 'hi', 'kn', 'ks', 'kok', 'mai', 'ml', 'mr', 'nep', 'or', 'pa', 'sat', 'san', 'te', 'ur', 'sd', 'mni, ta, doi, 'bn', 'as', 'brx'] 

lang_unicodes = {'as': '[\u0980-\u09FF]+', 'mai': '[\u0900-\u097F]+', 'gu': '[\u0A80-\u0AFF]+', 'bn': '[\u0980-\u09FF]+',
            'hi': '[\u0900-\u097F]+', 'kn': '[\u0C80-\u0CFF]+', 'ks': '[\u0600-\u06FF]+', 'ml': '[\u0D00-\u0D7F]+',
            'mr': '[\u0900-\u097F]+', 'mni': '[\uABC0-\uABFF]+', 'nep': '[\u0900-\u097F]+', 'or': '[\u0B00-\u0B7F]+',
            'pa': '[\u0A00-\u0A7F]+', 'san': '[\u0900-\u097F]+', 'sat': '[\u1C50-\u1C7F]+', 'sd': '[\u0900-\u097F]+',
            'ta': '[\u0B80-\u0BFF]+', 'te': '[\u0C00-\u0C7F]+', 'ur': '[\u0600-\u06FF]+', 'brx': '[\u0900-\u097F]+',
            'kok': '[\u0900-\u097F]+', 'doi': '[\u0900-\u097F]+'}

def is_english_alphabet(char):
    return ord('a') <= ord(char.lower()) <= ord('z')

def process_sentence(sentence, num_uni, lang_uni):
    should_keep = False
    cleaned_sentence = ""
    reasons = ""

    for char in sentence:
        if char in ["′", "′", "'", "'", "ʼ", "'", "`"]:
            char = "'"
        if char in ['"', '"']:
            char = '"'
        if char == ";":
            char = ","
        if char == "؛":
            char = "،"
            
                    
        if char in all_symbols or is_english_alphabet(char) or char.isdigit() or num_uni.match(char) or lang_uni.match(char):
            if char not in symbols_silent and (not lang_uni.match(char)) and char.strip() != "":
                should_keep = True
                reasons += char + " "
            elif num_uni.match(char):
                should_keep = True
                reasons += char + " "
        elif char.strip() != "" and ord(char) not in [8204, 8203, 8205]:
            should_keep = True
            reasons += char + " "

        cleaned_sentence += char
    return cleaned_sentence, should_keep, reasons


###
combined_data = []

path_1 = f'/home/tts/ttsteam/datasets/indic_clean_texts/final_sentences/9k_sentences/combined/{language}.txt'
output_path = f'/home/tts/ttsteam/datasets/indic_clean_texts/final_sentences/new_sentences/extra_1500_{language}_sentences.txt'
path_2 = f'/home/tts/ttsteam/datasets/indic_clean_texts/final_sentences/9k_sentences/combined/{language}(old).txt'

def remove_quotes(sentence):
    sentence.replace('"', '').strip()
    sentence = re.sub(r'\s+', ' ', sentence)
    return sentence

if os.path.exists(path_1) and os.path.exists(path_2):
    lang_num = re.compile(lang_number_dict[language])
    lang_chars = re.compile(lang_unicodes[language])
    with open(path_1, 'r', encoding='utf-8') as file_1:
        data_1 = file_1.read()
        combined_data.extend(filter(None, map(remove_quotes, data_1.split('\n'))))

    data_2_sentences = {}
    with open(path_2, 'r', encoding='utf-8') as file_2:
        data_2 = file_2.read().splitlines() 
        data_2_sentences = []  

        for sentence in data_2:
            cleaned_sentence, should_keep, reasons = process_sentence(sentence, lang_num, lang_chars)
            if not should_keep:  
                data_2_sentences.append(cleaned_sentence)

    # Remove quotes from data_2
    data_2_sentences = [remove_quotes(sentence) for sentence in data_2_sentences]

    # Filter sentences from path_1 that are not present in path_2
    unique_data = []
    for sentence in combined_data:
            cleaned_sentence, should_keep, reasons = process_sentence(sentence, lang_num, lang_chars)
            if not should_keep and remove_quotes(cleaned_sentence) not in data_2_sentences:  
                unique_data.append(cleaned_sentence)

    # Write the unique sentences to the output file
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write('\n'.join(unique_data))

    print(f"Unique sentences for language have been written to {output_path}")
else:
    print("One or more paths do not exist.")

