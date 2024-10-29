'''
This script analyzes text data in the from specified data sources and languages.
It extracts and filters bigrams from text data, saving the filtered bigrams and sentences in separate files based on a frequency threshold.
'''

import os
import pandas as pd
from collections import Counter
import re
import string
from tqdm import tqdm

data_sources = ['wikisource']
data_path = '/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_texts_2'
languages = ['san']
freq = 10

# unicode values in this range will be discarded
lang_number_dict = {'as': '[\u09E6-\u09EF]+',
                    'bn': '[\u09E6-\u09EF]+',
                    'hi': '[\u0966-\u096F]+',
                    'mr': '[\u0966-\u096F]+',
                    'ta': '[\u0BE6-\u0BEF]+',
                    'te': '[\u0C66-\u0C6F]+',
                    'kn': '[\u0CE6-\u0CEF]+',
                    'ml': '[\u0D66-\u0D6F]+',
                    'or': '[\u0B66-\u0B6F]+',
                    'pa': '[\u0A66-\u0A6F]+',
                    'gu': '[\u0AE6-\u0AEF]+',
                    'mni':'[\uABF0-\uABF9]+',
                    'sa': '[\u0966-\u096F]+',
                    'ks': '[\u0660-\u0669]+',
                    'ur': '[\u0660-\u0669]+',
                    'mai': '[\u0966-\u096F]+',
                    'sd': '[\u0966-\u096F]+',
                    'nep': '[\u0966-\u096F]+',
                    'brx': '[\u0966-\u096F]+',
                    'kok': '[\u0966-\u096F]+',
                    'sat': '[\u1C50-\u1C59]+',}

# Unicode ranges for different languages
unicodes = {'as': (0x0980, 0x09FF), 'mai': (0x0900, 0x097F), 'gu': (0x0A80, 0x0AFF), 'bn': (0x0980, 0x09FF),
            'hi': (0x0900, 0x097F), 'kn': (0x0C80, 0x0CFF), 'ks': (0x0600, 0x06FF), 'ml': (0x0D00, 0x0D7F),
            'mr': (0x0900, 0x097F), 'mni': (0xABC0, 0xABFF), 'nep': (0x0900, 0x097F), 'or': (0x0B00, 0x0B7F),
            'pa': (0x0A00, 0x0A7F), 'san': (0x0900, 0x097F), 'sat': (0x1C50, 0x1C7F), 'sd': (0x0900, 0x097F),
            'ta': (0x0B80, 0x0BFF) , 'te': (0x0C00, 0x0C7F), 'ur': (0x0600, 0x06FF), 'brx':(0x0900, 0x097F),
            'kok':(0x0900, 0x097F), 'doi': (0x0900, 0x097F)}

ben_unicode_skip_list = ['\u0984', '\u098d', '\u098e', '\u0991', '\u0992', '\u09a9', '\u09b1', '\u09b3', '\u09b4', '\u09b5', '\u09ba', '\u09bb', '\u09c5', '\u09c6', '\u09c9', '\u09ca', '\u09cf', '\u09d0', '\u09d1', '\u09d2', '\u09d3', '\u09d4', '\u09d5', '\u09d6', '\u09d8', '\u09d9', '\u09da', '\u09db', '\u09de', '\u09e4', '\u09e5', '\u09ff', '\u200c']

def remove_chars_with_regex(input_string):
    pattern = '[' + re.escape(''.join(ben_unicode_skip_list)) + ']'
    return re.sub(pattern, '', input_string)

def remove_emoji(string):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

def remove_words_with_org(input_string):
    pattern = re.compile(r'\b\w*\.org.?\b')
    result = re.sub(pattern, '', input_string)
    return result

def remove_words_with_com(input_string):
    pattern = re.compile(r'\b\w*\.com.?\b')
    result = re.sub(pattern, '', input_string)
    return result

def has_indic_chars(input_string, unicode_range):
    for char in input_string:
        if char.isnumeric() or char.isspace() or char in string.punctuation or char in string.ascii_letters:
            continue
        if unicode_range[0] <= ord(char) <= unicode_range[1]:
            continue
        else:
            return False
    return True

def has_greek_letters(input_string):
    greek_pattern = re.compile('[Α-Ωα-ω]+')
    return bool(greek_pattern.search(input_string))

def split_indic_sentences(text):
    sentences = []
    current_sentence = ""
    for char in text:
        if char in ['।', '?', '!', '•', '◾', '✓', '●', '■', '·', '→', '৷', '.']: #.
            current_sentence += char
            sentences.append(current_sentence.strip())
            current_sentence = ""
        else:
            current_sentence += char
    if current_sentence:
        sentences.append(current_sentence.strip())
    return sentences

def clean_text(text, language):
    unicode = unicodes[language]
    text = text.replace('&quot', '')
    text = text.replace('Î²', '')
    text = text.replace('॥', '')
    text = text.replace('‚', '')
    text = text.replace('…','')
    text = text.replace('”', '')
    text = text.replace('“', '')
    text = text.replace('¸', '')
    replace_patterns = [r'\u200d', r'\u200c', r'\ufeff', r'\u200b', r'‎', r'██', r'', r'￼', r'ʼʼ', r'‘‘', r'‘', r'ʼ', r'۔', r'\. \.', r'−', r'ꠞ', r'·', r'–', r'®', r'°', r'₹', r'£']
    for pattern in replace_patterns:
        text = re.sub(pattern, ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = remove_emoji(text)
    text = remove_words_with_com(text)
    text = remove_words_with_org(text)
    text = text.replace('"', '')
    if (not has_greek_letters(text)) and ('ʋ' not in text) and ('ɐ' not in text) and ('t̺' not in text) and ('ɻ' not in text) and ('ā' not in text) and ('â' not in text) and ('Ã' not in text) and ('Â' not in text):
        if language=='hi' and ('ऽ' in text):
            text = ''
        return text
    return ''

def remove_special_characters(text, language):
    text = re.sub(r'[a-zA-Z]+', '', text)
    if language == "sd":
        text = re.sub(r'[()\[\]{}!@#$%&*~/\\=+x\/\-⁄_<>|,.?;:‚‡ÅÃÂ…−٪،¡≤«»©¥„﻿…।¹‡|॥−á¹`–—°ʋɐːt̺upuɻɐ‏‎؜āαβÎ²￼â€™武俠俠小小說慧可武俠俠小小說®ᱻ]+', '', text)
        text = re.sub(r'[()\[\]{}@#$%&*~/\\=+\-–_—◾■✓·±Δ<>•●→;←^′°:…“”]', ' ', text)
    else:
        text = re.sub(r'[()\[\]{}!@#$%&*~/\\=+x\/\-⁄_<>|″,‚.?‡Å;:ÃÂ…−á¹٪،≤„¡©¥«»﻿…¹‡|॥−‘।”"”“\'`’′–—°ʋɐːt̺upuɻɐ‏‎؜āÎ²￼â€™武俠俠小小說慧可武俠俠小小說®ᱻ‘’]+', '', text)
        text = re.sub(r'[()\[\]{}@#$%&*~/\\=+\-–_—◾■✓·±Δ<>•●→;←^′°:…“”‘’"\'`]', ' ', text) #remove punctuations
    text = re.sub(r'\s+', ' ', text) # remove extra spaces
    text = re.sub(r'[1234567890]+', '', text)
    if (language == "bn" or language == "as"):
        text = remove_chars_with_regex(text)
    if language in lang_number_dict:
        text = re.sub(lang_number_dict[language], '', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def generate_ngrams(word, n):
    ngrams = []
    if (len(word)>=n):
        ngrams = ([''.join(word[i:i + n]) for i in range(len(word) - n + 1) if len(word[i:i + n]) == n])
    return ngrams

def ngrams_from_sentences(sentence, n, language):
    sentence = clean_text(sentence, language)
    sentence = remove_special_characters(sentence, language) #chnage, add cleaning text, etc.
    sentence.strip()
    words = (sentence.split())
    all_ngrams = []
    for word in words:
        all_ngrams.extend(generate_ngrams(word,n))
    return all_ngrams

def get_sentences():
    for language in languages:
        final_sentences = set()
        all_bigrams = {}
        reqd_bigrams = set()
        data_freq = {}

        # get all bigrams
        all_bigrams_path = '/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_raw/final/final_ngrams_dict/'
        bigram_csv = os.path.join(all_bigrams_path, language, 'bigram.csv')

        data = pd.read_csv(bigram_csv)
        for index, row in data.iterrows():
            all_bigrams[row['Bigram']] = row['Frequency']

        for bigram in all_bigrams:
            if all_bigrams[bigram] > freq:
                reqd_bigrams.add(bigram)
     
        # get all sentences
        data_files = []
        for data_source in data_sources:
            path = os.path.join(data_path, data_source, f'{language}.txt')
            if (os.path.exists(path)):
                data_files.append(path)
        print(data_files)
        sentences = []
        for file in tqdm(data_files):
            with open(file, 'r') as csv_file:
                lines = csv_file.readlines()
                for line in lines:
                    if len(line.split())>2:
                        lines = split_indic_sentences(line) 
                        for line in lines:
                            sentences.append(line.strip())

        # get filtered sentences
        for sentence in tqdm(sentences):
            sentence_bigrams_list = ngrams_from_sentences(sentence, 2, language)
            for sentence_bigram in sentence_bigrams_list:
                if sentence_bigram in reqd_bigrams:
                    final_sentences.append(sentence_bigram)
                            
        os.makedirs(f'/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_texts/final_sentences/wiki_sentences/{language}', exist_ok = True)
        path  = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_texts/final_sentences/wiki_sentences/{language}/{language}.txt' 
        pd.DataFrame(final_sentences).to_csv(path, mode='w', header=None, index=False)
        print(f'File saved to: {path}')
        os.makedirs(f'/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_texts/bigrams_over_10/{language}', exist_ok = True)
        bigrams_file = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_texts/bigrams_over_10/{language}/{language}.txt'
        
        with open(bigrams_file, 'w') as file:
            sorted_bigrams = sorted(list(reqd_bigrams), key=lambda x: all_bigrams[x], reverse=True)
            print (f'Bigram, Frequency', file = file)
            for bigram in sorted_bigrams:
                file.write(f'{bigram}, {all_bigrams[bigram]}\n')
        print(f'File saved to: {bigrams_file}')

get_sentences()




