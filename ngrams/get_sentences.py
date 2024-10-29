import pandas as pd
from collections import Counter, defaultdict
from tqdm import tqdm
import csv
import re
import os

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

def save_data(result_filepath_bi, result_bi, n):
    ngram = 'Bigram'
    if n == 3:
        ngram = 'Trigram'

    with open(result_filepath_bi, 'w', newline='') as csvfile:
        sorted_items = dict(sorted(result_bi.items(), key=lambda x: int(x[1]), reverse=True))
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([ngram, 'Count'])
        for key, value in sorted_items.items():
            csv_writer.writerow([key, value])
    print (f"Saved data for {result_filepath_bi}")

ben_unicode_skip_list = ['\u0984', '\u098d', '\u098e', '\u0991', '\u0992', '\u09a9', '\u09b1', '\u09b3', '\u09b4', '\u09b5', '\u09ba', '\u09bb', '\u09c5', '\u09c6', '\u09c9', '\u09ca', '\u09cf', '\u09d0', '\u09d1', '\u09d2', '\u09d3', '\u09d4', '\u09d5', '\u09d6', '\u09d8', '\u09d9', '\u09da', '\u09db', '\u09de', '\u09e4', '\u09e5', '\u09ff']

def remove_chars_with_regex(input_string):
    pattern = '[' + re.escape(''.join(ben_unicode_skip_list)) + ']'
    return re.sub(pattern, '', input_string)

def remove_special_characters(text, language):
    text = re.sub(r'[a-zA-Z]+', '', text)
    text = re.sub(r'[()\[\]{}!@#$%&*~/\\=+\-_<>,.?;:‘।”"“\'`’′–—°]+', '', text)
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
    sentence = remove_special_characters(sentence, language)
    sentence.strip()
    words = (sentence.split())
    all_ngrams = []
    for word in words:
        all_ngrams.extend(generate_ngrams(word,n))
    return all_ngrams

def get_sentence_list(ngrams_csv, sentence_file, target_sentence, high_freq_ngrams, ngram_dict_path, n=2):
    ngram_df = pd.read_csv(ngrams_csv, sep = ",", header = 0)
    real_freq_dict = {ngram_df.iloc[i]['Bigram']: ngram_df.iloc[i]['Frequency'] for i in range (len(ngram_df))}
    # high_freq_ngrams_df = pd.read_csv(high_freq_ngrams, sep = ",", header = 0)
    
    if (n == 2):
        ngram_set = set(ngram_df['Bigram'].values)  # set of missing bigrams
        # high_freq_ngrams_set = set(high_freq_ngrams_df['Bigram'].values) # set of missing bigrams high freq
    else:
        ngram_set = set(ngram_df['Trigram'].values)  # set of missing trigrams
        # high_freq_ngrams_set = set(high_freq_ngrams_df['Trigram'].values) # set of missing trigrams high freq
    
    ngram_filler = {ngram: 0 for ngram in ngram_set}

    with open(sentence_file, 'r') as file:
        language = file.split('.')[0]
        for line in tqdm(file, desc="Processing sentences", unit="lines", total=50841082):
            
            sentence = line.strip()
            words = sentence.split()
            if (len(words)>25 or len(words)<3):
                    continue
            
            sentence_ngrams = ngrams_from_sentences(sentence, n, language)
            freq_dict = {element: sentence_ngrams.count(element) for element in sentence_ngrams}
            common_ngram_freq = {key: value for key, value in freq_dict.items() if key in ngram_set}
            # high_freq_ngrams = {key: value for key, value in freq_dict.items() if key in high_freq_ngrams_set}

            if len(common_ngram_freq) > 0:  #remove this condition
                # if all(ngram_filler[key] >= 1 for key in common_ngram_freq.keys() if key not in high_freq_ngrams.keys()) and all(ngram_filler[key] >=5 for key in high_freq_ngrams.keys()):
                    # continue  # Skip the update if all keys already have values greater than 0
                if all(ngram_filler[key] >= 1 for key in common_ngram_freq.keys()):
                    continue

                for key, val in common_ngram_freq.items():
                    ngram_filler[key] +=val
                
                with open(target_sentence, 'a') as chosen_file:
                    print (sentence, file = chosen_file)
                # if all(value >= 1 for value in ngram_filler.values()) and all(ngram_filler[key]>=5 for key in high_freq_ngrams_set):
                if all(value >= 1 for value in ngram_filler.values()):
                    "All ngrams satisfied"
                    break
                else:
                    continue
    
    with open(ngram_dict_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        sorted_items = dict(sorted(ngram_filler.items(), key=lambda x: int(x[1]), reverse=True))
        if (n == 2):
            csv_writer.writerow(['Bigram', 'Count', 'RealFreq'])
        else:
            csv_writer.writerow(['Trigram', 'Count', 'RealFreq'])
        
        for key, value in sorted_items.items():
            csv_writer.writerow([key, value, real_freq_dict[key]])

def get_sentence_list_base(language, ngrams_csv, sentence_list, target_sentence_file, ngram_dict_path, n = 2):
    ngram_df = pd.read_csv(ngrams_csv, sep = ",", header = 0)
    real_freq_dict = {ngram_df.iloc[i]['Bigram']: ngram_df.iloc[i]['Frequency'] for i in range (len(ngram_df))}
    bigram_set = set(ngram_df['Bigram'].values)  # set of missing ngrams
    ngram_filler = {bigram: 0 for bigram in bigram_set}
    for i in tqdm(range(len(sentence_list))):
        line = sentence_list[i]
        sentence = line.strip()
        sentence_ngrams = ngrams_from_sentences(sentence, n, language)
        freq_dict = {element: sentence_ngrams.count(element) for element in sentence_ngrams}
        common_bigram_freq = {key: value for key, value in freq_dict.items() if key in bigram_set}

        if len(common_bigram_freq) > 0:
            for key, val in common_bigram_freq.items():
                ngram_filler[key] +=val
            
            with open(target_sentence_file, 'a') as chosen_file:
                print (sentence, file = chosen_file)

    with open(ngram_dict_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        sorted_items = dict(sorted(ngram_filler.items(), key=lambda x: int(x[1]), reverse=True))
        if (n == 2):
            csv_writer.writerow(['Bigram', 'Count', 'RealFreq'])
        else:
            csv_writer.writerow(['Trigram', 'Count', 'RealFreq'])
        for key, value in sorted_items.items():
            csv_writer.writerow([key, value, real_freq_dict[key]])
    return

def get_sentence_corpus(filepaths_list, ngrams_csv, target_sentence_file, ngram_dict_path,language):
    if (os.path.exists(ngrams_csv) == False):
        print (f'Not found: {ngrams_csv}')
        return
    
    ngram_df = pd.read_csv(ngrams_csv, sep = ",", header = 0)
    real_freq_dict = {ngram_df.iloc[i]['Bigram']: ngram_df.iloc[i]['Frequency'] for i in range (len(ngram_df))}
    ngram_set = set(ngram_df['Bigram'].values)  # set of missing bigrams
    ngram_filler = {ngram: 0 for ngram in ngram_set}
    bigram_sentence_dict = defaultdict(list)
    for filepath in filepaths_list:
        if (os.path.exists(filepath) == False):
            print (f'{filepath} not found')
            continue
        with open(filepath, 'r') as file:
            print (filepath)
            for line in tqdm(file, desc="Processing sentences"):
                sentence = line.strip()
                # words = sentence.split()
                # if (len(words)>60):
                #     continue
                
                sentence_ngrams = ngrams_from_sentences(sentence, 2, language)
                freq_dict = Counter(sentence_ngrams)
                common_ngram_freq = {key: real_freq_dict[key] for key in freq_dict.keys() if key in ngram_set}
                common_ngram_freq = dict(sorted(common_ngram_freq.items(), key=lambda item: item[1]))

                for bigram in common_ngram_freq.keys():
                    if (len(bigram_sentence_dict[bigram])>=10):
                        continue
                    else:
                        # [source_name]_Sentence
                        source_name = filepath.split('/')[-2]
                        sentence = f'[{source_name}]_{sentence}'
                        bigram_sentence_dict[bigram].append(sentence)
                        for key in common_ngram_freq.keys():
                            ngram_filler[key] += freq_dict[key]
                        break
        
    # with open(sangrah_sentence_file, 'r') as file:
    #     for line in tqdm(file, desc="Processing sentences", unit="lines", total=50841082):
    #         sentence = line.strip()
    #         words = sentence.split()
    #         if (len(words)>50 or len(words)<3):
    #                 continue
            
    #         sentence_ngrams = ngrams_from_sentences(sentence, 2)
    #         freq_dict = Counter(sentence_ngrams)
    #         common_ngram_freq = {key: real_freq_dict[key] for key in freq_dict.keys() if key in ngram_set}
    #         common_ngram_freq = dict(sorted(common_ngram_freq.items(), key=lambda item: item[1]))

    #         for bigram in common_ngram_freq.keys():
    #             if (len(bigram_sentence_dict[bigram])>=10):
    #                 continue
    #             else:
    #                 bigram_sentence_dict[bigram].append(sentence)
    #                 for key in common_ngram_freq.keys():
    #                     ngram_filler[key] += freq_dict[key]
    #                 break
    
    with open(target_sentence_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        header = ['Bigram'] + [f'Sentence_{i}' for i in range(1, 11)]
        csv_writer.writerow(header)
        
        for key, values in bigram_sentence_dict.items():
            row = [key] + values + [''] * (len(header) - len(values) - 1)
            csv_writer.writerow(row)

    with open(ngram_dict_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        sorted_items = dict(sorted(ngram_filler.items(), key=lambda x: int(x[1]), reverse=True))
        csv_writer.writerow(['Bigram', 'Count', 'RealFreq'])

        for key, value in sorted_items.items():
            csv_writer.writerow([key, value, real_freq_dict[key]])
    return

def get_missing_bi_tri_from_sentence(sentence_path, target_csv, bigrams_filepath, trigrams_filepath):
    df_tri = pd.read_csv(trigrams_filepath, sep = ',', header = 0)
    trigram_set = set(df_tri['Trigram'])

    df_bi = pd.read_csv(bigrams_filepath, sep = ',', header = 0)
    bigram_set = set(df_bi['Bigram'])
    # sent_df = pd.DataFrame(columns = ['Num','Bigrams', 'Trigrams', 'Sentence'])
    with open(target_csv, 'w', newline='', encoding = 'utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Num','Bigrams', 'Trigrams', 'Sentence'])
        with open(sentence_path, 'r') as file:
            for line in file:
                bigrams = ngrams_from_sentences(line.strip(),2)
                trigrams = ngrams_from_sentences(line.strip(),3)
                common_bigrams = bigrams.intersection(bigram_set)
                common_trigrams = trigrams.intersection(trigram_set)
                ngram_len =  len(common_bigrams) + len(common_trigrams)
                csv_writer.writerow([ngram_len, common_bigrams,common_trigrams,line.strip()])

    return

def get_wiki_sentence_corpus(wiki_sentence_file, ngrams_csv, target_sentence_file, ngram_dict_path):
    ngram_df = pd.read_csv(ngrams_csv, sep = ",", header = 0)
    real_freq_dict = {ngram_df.iloc[i]['Bigram']: ngram_df.iloc[i]['Frequency'] for i in range (len(ngram_df))}
    ngram_set = set(ngram_df['Bigram'].values)  # set of missing bigrams
    ngram_filler = {ngram: 0 for ngram in ngram_set}
    bigram_sentence_dict = defaultdict(list)

    with open(wiki_sentence_file, 'r') as file:
        for line in tqdm(file, desc="Processing sentences", unit="lines", total=1383908):
            sentence = line.strip()
            words = sentence.split()
            if (len(words)>50 or len(words)<3):
                    continue
            
            sentence_ngrams = ngrams_from_sentences(sentence, 2)
            freq_dict = Counter(sentence_ngrams)
            common_ngram_freq = {key: real_freq_dict[key] for key in freq_dict.keys() if key in ngram_set}
            common_ngram_freq = dict(sorted(common_ngram_freq.items(), key=lambda item: item[1]))

            for bigram in common_ngram_freq.keys():
                if (len(bigram_sentence_dict[bigram])>=10):
                    continue
                else:
                    bigram_sentence_dict[bigram].append(sentence)
                    for key in common_ngram_freq.keys():
                        ngram_filler[key] += freq_dict[key]
                    break


    with open(target_sentence_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        header = ['Bigram'] + [f'Sentence_{i}' for i in range(1, 11)]
        csv_writer.writerow(header)
        
        for key, values in bigram_sentence_dict.items():
            row = [key] + values + [''] * (len(header) - len(values) - 1)
            csv_writer.writerow(row)

    with open(ngram_dict_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        sorted_items = dict(sorted(ngram_filler.items(), key=lambda x: int(x[1]), reverse=True))
        csv_writer.writerow(['Bigram', 'Count', 'RealFreq'])

        for key, value in sorted_items.items():
            csv_writer.writerow([key, value, real_freq_dict[key]])
    return

# languages = ['as', 'bn', 'brx', 'doi', 'gu', 'hi', 'kn', 'ks', 'kok', 'mai', 'ml', 'mni', 'mr', 'nep', 'or', 'pa', 'san', 'sat', 'sd', 'ta', 'te', 'ur']




if __name__ == "__main__":


    languages = ['as', 'bn', 'brx', 'gu', 'hi', 'kn', 'ml', 'mni', 'mr', 'or', 'pa', 'ta', 'te']

    for language in languages:
        print(f"Processing for language: {language}")
        female_sentences = []
        male_sentences = []
        sentence_file = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indictts/{language}/metadata.csv'
        if (sentence_file.endswith('.csv')):
            language = sentence_file.split('/')[-2]
            indic_df = pd.read_csv(sentence_file, sep = '|')
            indic_df.columns = ['ID', 'text', 'speaker']

            for index, row in indic_df.iterrows():
                if row['speaker'] == "female":
                    female_sentences.append(row['text'])
                if row['speaker'] == "male":
                    male_sentences.append(row['text'])

        target_sentence_file = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_texts/missing_bigram_sentences/indic_tts/{language}/female_sentences.txt'
        ngrams_csv = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_texts/ngram_diff/{language}/bigram_diff.csv'
        ngram_dict_path = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_texts/missing_bigram_sentences/indic_tts/{language}/female_bigram.csv'
        get_sentence_list_base(language, ngrams_csv, female_sentences , target_sentence_file, ngram_dict_path, 2)

        target_sentence_file = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_texts/missing_bigram_sentences/indic_tts/{language}/male_sentences.txt'
        ngrams_csv = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_texts/ngram_diff/{language}/bigram_diff.csv'
        ngram_dict_path = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_texts/missing_bigram_sentences/indic_tts/{language}/male_bigram.csv'
        get_sentence_list_base(language, ngrams_csv, male_sentences , target_sentence_file, ngram_dict_path, 2)



