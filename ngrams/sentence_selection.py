import os
import pandas as pd
from collections import Counter
import re
import string
from tqdm import tqdm

bigram_freq = 12 #34

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
                    'mni': '[\uABF0-\uABF9]+',
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

def split_hindi_sentences(text):
    sentences = []
    current_sentence = ""
    for char in text:
        if char in ['।', '?', '!', '•', '◾', '✓', '●', '■', '·', '→', '.', '؟', '!', '۔']: #.
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
    # text = text.replace('୤', '')
    # text = text.replace('૥', '')
    replace_patterns = [r'\u200d', r'\u200c', r'\ufeff', r'\u200b', r'‎', r'██', r'', r'￼', r'ʼʼ', r'‘‘', r'‘', r'ʼ', r'۔', r'\. \.', r'−', r'ꠞ', r'·', r'–', r'®', r'°', r'₹', r'£']
    for pattern in replace_patterns:
        text = re.sub(pattern, ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = remove_emoji(text)
    text = remove_words_with_com(text)
    text = remove_words_with_org(text)
    text = text.replace('😏', '')
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

base_path = '/home/tts/ttsteam/datasets/indic_clean_raw/final/final_ngrams_dict/'
# languages = ['gu', 'hi', 'kn', 'ks', 'kok', 'mai', 'ml', 'mr', 'nep', 'or', 'pa', 'sat', 'san', 'te', 'ur', 'sd', 'mni, ta, doi, 'bn', 'as', 'brx'] 
languages = ['mni'] 

data_path = '/home/tts/ttsteam/datasets/indic_clean_texts_2'
data_sources = ['bpcc', 'asr-codemixed', 'mkb_parallel', 'nios', 'pib', 'pratham', 'shoonya', 'ugc-resources', 'vanipedia', 'isha-foundation', 'wiki', 'wikisource']
# data_sources = ['asr-codemixed', 'mkb_parallel', 'neutral_recording_sentences', 'nios', 'pib', 'pratham', 'shoonya', 'ugc-resources', 'vanipedia', 'isha-foundation']

def get_final_sentences():
    word_count = {'Language':[], 'Total_Word_Count':[], 'Unique_Words_Count':[]}

    for language in languages:
        num_words = 0
        word_set = set()
        base_path = '/home/tts/ttsteam/datasets/indic_clean_raw/final/final_ngrams_dict/'
        bigram_csv = os.path.join(base_path, language, 'bigram.csv')

        all_bigrams = {}
        high_freq_bigrams = set()
        low_freq_bigrams = set()

        data_freq = {}
        final_sentence_list = set()

        data = pd.read_csv(bigram_csv)
        for index, row in data.iterrows():
            all_bigrams[row['Bigram']] = row['Frequency']
            data_freq[row['Bigram']] = 0  # data frequency will maintain the frequency of seen bigrams from sentences
            if (row['Frequency']>=10):
                high_freq_bigrams.add(row['Bigram'])
            else:
                low_freq_bigrams.add(row['Bigram'])

        bigram_tracker = high_freq_bigrams | low_freq_bigrams   # union of high_freq and low_freq_bigrams - remove this line

        data_files = []
        for data_source in data_sources:
            path = os.path.join(data_path, data_source, f'{language}.txt')
            if (os.path.exists(path)):
                data_files.append(path)
        print(data_files)
        
        sentences = []
        for file in tqdm(data_files):
            # source = file.split('/')[-2]
            with open(file, 'r') as csv_file:
                lines = csv_file.readlines()
                for line in lines:
                    lines = split_hindi_sentences(line) 
                    for line in lines:
                        if (len(line.split())>2):
                            sentences.append(line.strip())

        for sentence in tqdm(sentences):
            sentence_high_freq_bigram = set()
            sentence_low_freq_bigram = set()
            sentence_bigrams_list = ngrams_from_sentences(sentence, 2, language)
            sentence_bigrams_counter = Counter(sentence_bigrams_list) 
            for i in sentence_bigrams_counter.keys():
                if i in high_freq_bigrams:
                    sentence_high_freq_bigram.add(i)
                elif i in low_freq_bigrams:
                    sentence_low_freq_bigram.add(i)

            min_threshold = 8
            if (len(sentence_high_freq_bigram) >= min_threshold or len(sentence_low_freq_bigram) != 0):

                words = sentence.split()
                if len(words)<=45 and len(words)>2:
                    for i in sentence_high_freq_bigram:
                        # try:
                        #     bigram_tracker.remove(i)
                        # except:
                        #     pass
                        data_freq[i] = data_freq[i] + sentence_bigrams_counter[i]
                        if (data_freq[i] >= bigram_freq): 
                            high_freq_bigrams.remove(i)
                    for i in sentence_low_freq_bigram:
                        # try:
                        #     bigram_tracker.remove(i)
                        # except:
                        #     pass
                        data_freq[i] = data_freq[i] + sentence_bigrams_counter[i]
                        if (data_freq[i] >= all_bigrams[i]):
                            low_freq_bigrams.remove(i)
                    if sentence.strip()!='' and len(sentence.split())<=40:
                        final_sentence_list.add(sentence.strip())
                        num_words += len(words)
                        word_set.update(set(words))

                if (len(high_freq_bigrams) == 0 and len(low_freq_bigrams) == 0):
                    print ("found all bigrams")
                    break

        # Word count and unique words count for a specific language.
        word_count['Language'].append(language)
        word_count['Total_Word_Count'].append(num_words)
        word_count['Unique_Words_Count'].append(len(word_set))
# /home/tts/ttsteam/datasets/indic_clean_texts/final_sentences/9k_sentences/combined/doi.txt
        os.makedirs('/home/tts/ttsteam/datasets/indic_clean_texts/final_sentences/9k_sentences/', exist_ok = True)
        path_1 = f'/home/tts/ttsteam/datasets/indic_clean_texts/final_sentences/9k_sentences/{language}.txt'
        pd.DataFrame(final_sentence_list).to_csv(path_1, mode='w', header=None, index=False)
        print(f'Sentences saved to: {path_1}')

        if (len(high_freq_bigrams)!=0 or len(low_freq_bigrams)!=0):
            os.makedirs(f'/home/tts/ttsteam/datasets/indic_clean_texts/final_missing_bigrams/{language}/', exist_ok = True)        
            missing_bigrams_file = f'/home/tts/ttsteam/datasets/indic_clean_texts/final_missing_bigrams/{language}/{language}.txt'

            with open(missing_bigrams_file, 'w') as file:
                combined_bigrams = bigram_tracker.union(low_freq_bigrams)
                sorted_bigrams = sorted(combined_bigrams, key=lambda x: all_bigrams[x], reverse=True)
                file.write("Bigram, Frequency\n")
                for bigram in sorted_bigrams:
                    file.write(f'{bigram}, {all_bigrams[bigram]}\n')
        
    path_2  = '/home/tts/ttsteam/datasets/indic_clean_texts/final_sentences/word_count.txt'
    pd.DataFrame(word_count).to_csv(path_2, mode='w', index=False)
    print(f'Word count saved to: {path_2}')

def get_missing_bigrams_sentences():
    for language in languages:
        #initialize
        final_sentences = set()
        all_bigrams = {}  
        missing_bigrams = set()
        data_freq = {}

        # get all bigrams
        all_bigrams_path = '/home/tts/ttsteam/datasets/indic_clean_raw/final/final_ngrams_dict/'
        bigram_csv = os.path.join(all_bigrams_path, language, 'bigram.csv')

        data = pd.read_csv(bigram_csv)
        for index, row in data.iterrows():
            all_bigrams[row['Bigram']] = row['Frequency']

        # get missing bigrams
        missing_bigrams_path = f'/home/tts/ttsteam/datasets/indic_clean_texts/final_missing_bigrams/{language}'
        missing_bigram_csv = os.path.join(missing_bigrams_path, f'{language}.txt')
        data = pd.read_csv(missing_bigram_csv)
        missing_bigrams = (data["Bigram"].values)
        missing_bigrams = set(missing_bigrams)
        # get all sentences
        data_files = []
        for data_source in data_sources:
            path = os.path.join(data_path, data_source, f'{language}.txt')
            if (os.path.exists(path)):
                data_files.append(path)
        sentences = []
        for file in tqdm(data_files):
            with open(file, 'r') as csv_file:
                lines = csv_file.readlines()
                for line in lines:
                    if len(line.split())>2:
                        lines = split_hindi_sentences(line) 
                        for line in lines:
                            sentences.append(line.strip())
                            # sentences.append(f'{line.strip()} -> {source}')

        bigram_tracker = missing_bigrams
        # get filtered sentences
        for sentence in tqdm(sentences):
            sentence_bigrams_list = ngrams_from_sentences(sentence, 2, language)
            sentence_bigrams_counter = Counter(sentence_bigrams_list)
            sentence_missing_bigrams = missing_bigrams & set(sentence_bigrams_list)
            if (len(sentence_missing_bigrams)!=0):
                if len(sentence.split())>2 and sentence.strip()!='':
                    final_sentences.add(sentence.strip())
                    for bi in sentence_missing_bigrams:
                        try:
                            bigram_tracker.remove(bi)
                        except Exception:
                            pass
                        if bi not in data_freq.keys():
                            data_freq[bi] = sentence_bigrams_counter[bi]
                        else:
                            data_freq[bi] += sentence_bigrams_counter[bi]

                    if (data_freq[bi]>=all_bigrams[bi]):
                        if bi in missing_bigrams: 
                            missing_bigrams.remove(bi)
                            
        os.makedirs(f'/home/tts/ttsteam/datasets/indic_clean_texts/final_sentences/9k_sentences/{language}', exist_ok = True)
        path  = f'/home/tts/ttsteam/datasets/indic_clean_texts/final_sentences/9k_sentences/{language}/{language}_v2.txt' 
        pd.DataFrame(final_sentences).to_csv(path, mode='w', header=None, index=False)
        print(f'File saved to: {path}')
        os.makedirs(f'/home/tts/ttsteam/datasets/indic_clean_texts/final_missing_bigrams/{language}', exist_ok = True)
        missing_bigrams_file = f'/home/tts/ttsteam/datasets/indic_clean_texts/final_missing_bigrams/{language}/{language}_v2.txt'
        
        with open(missing_bigrams_file, 'w') as file:
            sorted_bigrams = sorted(list(bigram_tracker), key=lambda x: all_bigrams[x], reverse=True)
            print ('Bigram, Frequency', file = file)
            for bigram in sorted_bigrams:
                file.write(f'{bigram}, {all_bigrams[bigram]}\n')

get_final_sentences()
get_missing_bigrams_sentences()