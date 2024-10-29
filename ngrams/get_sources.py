import os
import pandas as pd
from collections import Counter
import re
import string
from tqdm import tqdm
import csv 

languages = ['mr'] 

data_path = '/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_texts_2'
data_sources = ['asr-codemixed', 'mkb_parallel', 'neutral_recording_sentences', 'nios', 'pib', 'pratham', 'shoonya', 'ugc-resources', 'vanipedia', 'isha-foundation', 'wiki', 'wikisource']

def split_indic_sentences(text):
    sentences = []
    current_sentence = ""
    for char in text:
        if char in ['।', '?', '!', '•', '◾', '✓', '●', '■', '·', '→', '৷', '.']: #remove '.' if the language contains poornvirams.
            current_sentence += char
            sentences.append(current_sentence.strip())
            current_sentence = ""
        else:
            current_sentence += char
    if current_sentence:
        sentences.append(current_sentence.strip())
    return sentences

def get_sources():
    for language in languages:
        sentence_source = {}
        data_files = []
        for data_source in data_sources:
            path = os.path.join(data_path, data_source, f'{language}.txt')
            if (os.path.exists(path)):
                data_files.append(path)

        sentences = []
        for file in tqdm(data_files):
            source = file.split('/')[-2]
            with open(file, 'r') as csv_file:
                lines = csv_file.readlines()
                for line in lines:
                    lines = split_indic_sentences(line)
                    for line in lines:
                        line = re.sub(r'[“‘’”]', "'", line.replace('|', '।').replace(',', '').replace("'", '').replace('"', ''))
                        line = re.sub(r'\s+', ' ', line)
                        if line.strip():
                            sentences.append(line.strip())
                        source = source.replace('"', '').strip()
                        if source not in sentence_source:
                            sentence_source[source] = []
                        sentence_source[source].append(line.strip())

    all_sentences_file = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_final_sources/wiki/{language}/all_sentence_sources.csv'
    with open(all_sentences_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Sentence', 'Source'])
        for source, sentences in sentence_source.items():
            for sentence in sentences:
                print (sentence, source, file = file)
                # writer.writerow([sentence, source])

    check_sentences = []
    order_list = []
    original_sentences = []

    data_file = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_final_sources/wiki/{language}/sentences.txt'
    # data_file = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_texts/specific_languages/san/male/final_sentences.txt'
    with open(data_file, 'r') as csv_file:
            lines = csv_file.readlines()
            for line in lines:
                line = re.sub(r'\s+', ' ', line) 
                line = re.sub(r'[“‘’”]', "'", line.replace('|', '।').replace('"', ''))
                original_sentences.append(line.strip())  
                line = re.sub(r'[,\']', '', line).strip()
                line = re.sub(r'\s+', ' ', line)
                check_sentences.append(line.strip())
        
    for i in tqdm(range(len(check_sentences))):
        found=False
        for source, values in sentence_source.items():
            if check_sentences[i] in {v for v in values}:
                found=True
                # if source not in check_sources:
                #     check_sources[source] = []
                # check_sources[source].append(sentence.strip())
                order_list.append((original_sentences[i], source))
                break
        if not found:
            # check_sources['unknown'].append(sentence.strip())
            order_list.append((original_sentences[i], 'unknown'))
        
        output_path = f'/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_final_sources/wiki/{language}/sentence_sources.csv'
        with open(output_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Sentence', 'Source'])
            for sentence, source in order_list:
                sentence = sentence.replace('"', '')
                sentence = re.sub(r'\s+', ' ', sentence)
                if sentence.strip():
                    writer.writerow([sentence, source])

get_sources()




