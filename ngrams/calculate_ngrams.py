from collections import Counter
import itertools
from multiprocessing import Pool
import re
from tqdm import tqdm
import pandas as pd
import string
import csv

from utils import has_unicode_characters

def remove_extra_chars_util(input_string):
    unicode_range_pattern = re.compile('[\u0020\u0980-\u09FF]+', flags=re.UNICODE)
    result_string= ''.join(unicode_range_pattern.findall(input_string))
    result_string = re.sub(r'\s+', ' ', result_string) 
    result_string = result_string.replace('\n', ' ')
    return result_string

def remove_eng_extra_chars(sentence):
    lowercase_sentence = str(sentence).lower()
    additional_chars_to_remove = "$#@"
    translator = str.maketrans('', '', string.punctuation + additional_chars_to_remove)
    no_special_chars_sentence = lowercase_sentence.translate(translator)
    return no_special_chars_sentence

def remove_extra_chars(recording_path):
    target_file = recording_path.split('.')[0] + '_cleaned.txt'
    new_lines = []
    with open(recording_path, 'r') as file:
        for line in file:
            new_lines.append(remove_extra_chars_util(line))
    
    with open (target_file, 'w') as new_file:
        for line in new_lines:
            print (line.strip(), file = new_file)
    
    return target_file

def save_data(result_filepath_bi, result_bi, n):
    ngram = 'Bigram'
    if n == 3:
        ngram = 'Trigram'

    with open(result_filepath_bi, 'w', newline='') as csvfile:
        sorted_items = dict(sorted(result_bi.items(), key=lambda x: int(x[1]), reverse=True))
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([ngram, 'Count'])
        for key, value in sorted_items.items():
            if has_unicode_characters(key) == False:
                csv_writer.writerow([key, value])
    print (f"Saved data for {result_filepath_bi}")

def generate_ngrams_util(word, n):
    ngrams = []
    if (len(word)>=n):
        ngrams = [''.join(word[i:i + n]) for i in range(len(word) - n + 1) if len(word[i:i + n]) == n]
    return ngrams

def count_ngrams_from_dictionary(chunk, n):
    data_list = chunk.split()
    vocab = Counter(data_list)
    ngrams_dict = Counter()
    for key, value in vocab.items():
        ngram_list = generate_ngrams_util(key, n)
        for i in ngram_list:
            if i in ngrams_dict.keys():
                ngrams_dict[i] += value
            else:
                ngrams_dict[i] = value
    return ngrams_dict

def merge_counters(counters):
    # Merge multiple Counters into one
    result = Counter()
    for counter in counters:
        result.update(counter)
    return result

def count_ngrams_dict(file_path, n, result_text_file, chunk_size=100000, num_processes=4):
    chunks = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for chunk in tqdm(iter(lambda: file.read(chunk_size), ''), desc="creating vocab"):
            chunks.append(chunk)

    with Pool(num_processes) as pool:
        counters = pool.starmap(count_ngrams_from_dictionary, [(chunk, n) for chunk in chunks])
    result_dict = merge_counters(counters)
    save_data(result_text_file, result_dict, n)
    return result_dict

# def dogri():
#     dict_main_2 = Counter()
#     dict_main_3 = Counter()

#     # Rasa Wiki
#     wiki = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/dogri/dogri_recording_wiki.txt' 
#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/dogri/wiki_{i}.txt'
#         result = count_ngrams_dict(wiki, i, result_filepath)
#         if (i == 2):
#             # dict_main_2 = Counter(dict_main_2) + Counter(result)
#             dict_main_2 += result
#         elif (i == 3):
#             # dict_main_3 = Counter(dict_main_3) + Counter(result)
#             dict_main_3 += result
   
#     # All Rasa
#     recording = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/dogri/dogri_recording.txt'
#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/dogri/recordings_{i}.txt'
#         result = count_ngrams_dict(recording, i, result_filepath)
#         if (i == 2):
#             # dict_main_2 = Counter(dict_main_2) + Counter(result)
#             dict_main_2 += result
#         elif (i == 3):
#             # dict_main_3 = Counter(dict_main_3) + Counter(result)
#             dict_main_3 += result
    
#     # Shoonya
#     shoonya = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/dogri/dogri_shoonya.txt'
#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/dogri/shoonya_{i}.txt'
#         result = count_ngrams_dict(shoonya, i, result_filepath)
#         if (i == 2):
#             dict_main_2 += result
#         elif (i == 3):
#             dict_main_3 += result

#     # Sangrah
#     sangrah = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/dogri/sangrah.txt'
#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/dogri/sangrah_{i}.txt'
#         result = count_ngrams_dict(sangrah, i, result_filepath)
#         if (i == 2):
#             dict_main_2 += result
#         elif (i == 3):
#             dict_main_3 += result


#     all_data_2 = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/dogri/all_data_2.txt'
#     save_data(all_data_2, dict_main_2)

#     all_data_3 = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/dogri/all_data_3.txt'
#     save_data(all_data_3, dict_main_3)
#     return

# def hindi():
#     dict_main_2 = Counter()
#     dict_main_3 = Counter()

#     # Rasa Wiki
#     wiki = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/hindi/recording_script_wiki.txt' 
#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/hindi/wiki_{i}.txt'
#         result = count_ngrams_dict(wiki, i, result_filepath)
#         if (i == 2):
#             # dict_main_2 = Counter(dict_main_2) + Counter(result)
#             dict_main_2 += result
#         elif (i == 3):
#             # dict_main_3 = Counter(dict_main_3) + Counter(result)
#             dict_main_3 += result
   
#     # All Rasa
#     recording = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/hindi/all_recording_script.txt'
#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/hindi/recordings_{i}.txt'
#         result = count_ngrams_dict(recording, i, result_filepath)
#         if (i == 2):
#             # dict_main_2 = Counter(dict_main_2) + Counter(result)
#             dict_main_2 += result
#         elif (i == 3):
#             # dict_main_3 = Counter(dict_main_3) + Counter(result)
#             dict_main_3 += result
    
#     # IndicTTS - Female
#     indic_tts_f = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/hindi/indictts_female.txt'
#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/hindi/indictts_fe_{i}.txt'
#         result = count_ngrams_dict(indic_tts_f, i, result_filepath)
#         if (i == 2):
#             # dict_main_2 = Counter(dict_main_2) + Counter(result)
#             dict_main_2 += result
#         elif (i == 3):
#             # dict_main_3 = Counter(dict_main_3) + Counter(result)
#             dict_main_3 += result

#     # IndicTTS - Male
#     indic_tts_m = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/hindi/indictts_male.txt'
#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/hindi/indictts_ma_{i}.txt'
#         result = count_ngrams_dict(indic_tts_m, i, result_filepath)
#         if (i == 2):
#             # dict_main_2 = Counter(dict_main_2) + Counter(result)
#             dict_main_2 += result
#         elif (i == 3):
#             # dict_main_3 = Counter(dict_main_3) + Counter(result)
#             dict_main_3 += result

#     # indicCorp - Hindi
#     indic_corp = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/hindi/indiccorp.txt'
#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/hindi/indic_corp_{i}.txt'
#         result = count_ngrams_dict(indic_corp, i, result_filepath)
#         if (i == 2):
#             dict_main_2 += result
#         elif (i == 3):
#             dict_main_3 += result

#     # Sangrah - Hindi
#     sangrah = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/hindi/sangrah.txt'
#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/hindi/sangrah_{i}.txt'
#         result = count_ngrams_dict(sangrah, i, result_filepath)
#         if (i == 2):
#             dict_main_2 += result
#         elif (i == 3):
#             dict_main_3 += result


#     all_data_2 = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/hindi/all_data_2.txt'
#     save_data(all_data_2, dict_main_2)

#     all_data_3 = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/hindi/all_data_3.txt'
#     save_data(all_data_3, dict_main_3)

#     return 

# def assamese():
#     dict_main_2 = Counter()
#     dict_main_3 = Counter()
#     # indicCorp - Assamese
#     indic_corp = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/assamese/indiccorp.txt'
#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/assamese/indic_corp_{i}.txt'
#         result = count_ngrams_dict(indic_corp, i, result_filepath)
#         if (i == 2):
#             dict_main_2 += result
#         elif (i == 3):
#             dict_main_3 += result

#     # Sangrah
#     sangrah = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/assamese/sangrah.txt'
#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/assamese/sangrah_{i}.txt'
#         result = count_ngrams_dict(sangrah, i, result_filepath)
#         if (i == 2):
#             dict_main_2 += result
#         elif (i == 3):
#             dict_main_3 += result

#     # Rasa Wiki
#     wiki = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/assamese/recording_script_wiki.txt' 
#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/assamese/wiki_{i}.txt'
#         result = count_ngrams_dict(wiki, i, result_filepath)
#         if (i == 2):
#             dict_main_2 += result
#         elif (i == 3):
#             dict_main_3 += result
   
#     # All Rasa
#     recording = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/assamese/all_recording_script.txt'
#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/assamese/recordings_{i}.txt'
#         result = count_ngrams_dict(recording, i, result_filepath)
#         if (i == 2):
#             dict_main_2 += result
#         elif (i == 3):
#             dict_main_3 += result
    
#     # IndicTTS - Female
#     indic_tts_f = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/assamese/indictts_female.txt'
#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/assamese/indictts_fe_{i}.txt'
#         result = count_ngrams_dict(indic_tts_f, i, result_filepath)
#         if (i == 2):
#             dict_main_2 += result
#         elif (i == 3):
#             dict_main_3 += result

#     # IndicTTS - Male
#     indic_tts_m = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/assamese/indictts_male.txt'
#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/assamese/indictts_ma_{i}.txt'
#         result = count_ngrams_dict(indic_tts_m, i, result_filepath)
#         if (i == 2):
#             dict_main_2 += result
#         elif (i == 3):
#             dict_main_3 += result

#     all_data_2 = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/assamese/all_data_2.txt'
#     save_data(all_data_2, dict_main_2)

#     all_data_3 = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/assamese/all_data_3.txt'
#     save_data(all_data_3, dict_main_3)
#     return

# def bengali():
#     # dict_main_2 = Counter()
#     # dict_main_3 = Counter()
    
#     # # indicCorp - Bengali
#     # indic_corp = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/bengali/indiccorp.txt'
#     # for i in [2,3]:
#     #     result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/bengali/indic_corp_{i}.txt'
#     #     result = count_ngrams_dict(indic_corp, i, result_filepath)
#     #     if (i == 2):
#     #         dict_main_2 = dict_main_2 + result
#     #     elif (i == 3):
#     #         dict_main_3 = dict_main_3 + result

#     # # Sangrah - Bengali
#     # sangrah = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/bengali/sangrah.txt'
#     # for i in [2,3]:
#     #     result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/bengali/sangrah_{i}.txt'
#     #     result = count_ngrams_dict(sangrah, i, result_filepath)
#     #     if (i == 2):
#     #         dict_main_2 = dict_main_2 + result
#     #     elif (i == 3):
#     #         dict_main_3 = dict_main_3 + result

#     # # Rasa Wiki
#     # wiki = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/bengali/recording_script_wiki.txt' 
#     # for i in [2,3]:
#     #     result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/bengali/wiki_{i}.txt'
#     #     result = count_ngrams_dict(wiki, i, result_filepath)
#     #     if (i == 2):
#     #         dict_main_2 = dict_main_2 + result
#     #     elif (i == 3):
#     #         dict_main_3 = dict_main_3 + result
   
#     # All Rasa
#     recording = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/bengali/recording_sentences.txt'
#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/bengali/recordings_15dec_{i}.txt'
#         result = count_ngrams_dict(recording, i, result_filepath)
#         # if (i == 2):
#         #     dict_main_2 = dict_main_2 + result
#         # elif (i == 3):
#         #     dict_main_3 = dict_main_3 + result
#     # import os
#     # folder = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/bengali/sentence_sampling_40/'
    
#     # for file in os.listdir(folder):
#     #     if file.startswith('2k_sentences_short.txt'):
#     #         recording = os.path.join(folder, file)
#     #         recording = remove_extra_chars(recording)
#     # # recording = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/tamil/tamil_recording_data.txt'
#     #         for i in [2,3]:
#     #             result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/bengali/sentence_samples/ngram_{file.split(".")[0]}_{i}_new.txt'
#     #             result = count_ngrams_dict(recording, i, result_filepath)
#         # if (i == 2):
#         #     dict_main_2 = dict_main_2 + result
#         # elif (i == 3):
#         #     dict_main_3 = dict_main_3 + result


#     # new_sentences = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/bengali/chosen_sentences_bigram.txt'

#     # for i in [2,3]:
#     #     result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/bengali/new_sentences_bigram{i}.txt'
        
#     #     result = count_ngrams_dict(new_sentences, i, result_filepath)
#     #     if (i == 2):
#     #         dict_main_2 = dict_main_2 + result
#     #     elif (i == 3):
#     #         dict_main_3 = dict_main_3 + result

#     # # IndicTTS - Female
#     # indic_tts_f = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/bengali/indictts_female.txt'
#     # for i in [2,3]:
#     #     result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/bengali/indictts_fe_{i}.txt'
#     #     result = count_ngrams_dict(indic_tts_f, i, result_filepath)
#     #     if (i == 2):
#     #         dict_main_2 = dict_main_2 + result
#     #     elif (i == 3):
#     #         dict_main_3 = dict_main_3 + result

#     # # IndicTTS - Male
#     # indic_tts_m = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/bengali/indictts_male.txt'
#     # for i in [2,3]:
#     #     result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/bengali/indictts_ma_{i}.txt'
#     #     result = count_ngrams_dict(indic_tts_m, i, result_filepath)
#     #     if (i == 2):
#     #         dict_main_2 = dict_main_2 + result
#     #     elif (i == 3):
#     #         dict_main_3 = dict_main_3 + result

#     # all_data_2 = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/bengali/new_recording_data_2_bigram.txt'
#     # save_data(all_data_2, dict_main_2)

#     # all_data_3 = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/bengali/new_recording_3_bigram.txt'
#     # save_data(all_data_3, dict_main_3)

#     return 

# def tamil():
#     dict_main_2 = Counter()
#     dict_main_3 = Counter()

#     sangrah = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/tamil/sangrah.txt'
#     folder = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/tamil/'


#     import os
#     os.makedirs(folder, exist_ok = True)

#     recording = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/tamil/tamil_recording.txt'
#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/tamil/recordings_{i}.txt'
#         result = count_ngrams_dict(recording, i, result_filepath)
#         if (i == 2):
#             # dict_main_2 = Counter(dict_main_2) + Counter(result)
#             dict_main_2 += result
#         elif (i == 3):
#             # dict_main_3 = Counter(dict_main_3) + Counter(result)
#             dict_main_3 += result


#     for i in [2,3]:
#         result_filepath = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/tamil/sangrah_{i}.txt'
#         result = count_ngrams_dict(sangrah, i, result_filepath)
#         if (i == 2):
#             dict_main_2 = dict_main_2 + result
#         elif (i == 3):
#             dict_main_3 = dict_main_3 + result

#     all_data_2 = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/tamil/sangrah_recording_2.txt'
#     save_data(all_data_2, dict_main_2)

#     all_data_3 = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/tamil/sangrah_recording_3.txt'
#     save_data(all_data_3, dict_main_3)

#     return 

# def english():
#     ljspeech = '/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/LJSpeech-1.1/metadata.csv'
#     df = pd.read_csv(ljspeech, sep = '|')
#     df.columns = ["ID", "Sentence", "NormSentence"]
#     sentences = df['NormSentence'].dropna().values
    
#     for i in range (len(sentences)):    
#         sentences[i] = remove_eng_extra_chars(sentences[i])
#     text = ''.join(sentences)
#     ljspeech_corpus = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/data_out/english/ljspeech.txt'
#     with open(ljspeech_corpus, 'w') as file:
#         print (text, file = file)
#     for i in [2,3]:
#         result_filepath  = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngrams_scripts/ngrams/english/ljspeech_{i}.'
#         count_ngrams_dict(ljspeech_corpus, i, result_filepath)
# # hindi()
# # assamese()
# # dogri()
# # bengali()
# english()
# # tamil()