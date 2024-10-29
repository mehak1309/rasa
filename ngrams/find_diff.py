import pandas as pd
import csv
import os
from utils import has_empty_unicode_characters

def find_diff(file1, file2, target_file):
    df_1 = pd.read_csv(file1, header = 0)
    content_dict_1 = dict(zip(df_1['Bigram'], df_1['Frequency']))

    df_2 = pd.read_csv(file2, header = 0)
    content_dict_2 = dict(zip(df_2['Bigram'], df_1['Frequency']))

    keys_difference = set(content_dict_1.keys()) - set(content_dict_2.keys())
    
    output_dict = dict()
    for key in keys_difference:
        output_dict[key] = content_dict_1[key]
    
    character_to_remove = '।'
    filtered_dict = {key: value for key, value in output_dict.items() if character_to_remove not in key}

    sorted_items = dict(sorted(filtered_dict.items(), key=lambda x: int(x[1]), reverse=True))
    with open(target_file, 'w', newline='', encoding = 'utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Bigram', 'Frequency'])
        for key, value in sorted_items.items():
            if has_empty_unicode_characters(key) == False:
                csv_writer.writerow([key, value])

if __name__ == "__main__":

    # global_bigrams_parent = '/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_raw/final/final_ngrams_dict/'
    # recording_bigrams_parent = '/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_texts/recordings_v0_dictionary'
    target_parent_folder = '/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_texts/final/ngram_diff_new/'
    os.makedirs(target_parent_folder, exist_ok = True)
    # languages = ['as', 'bn', 'brx', 'doi', 'gu', 'hi', 'kn', 'ks', 'kok', 'mai','ml', 'mni', 'mr', 'nep', 'or', 'pa', 'san', 'sat', 'sd', 'ta', 'te','ur']
    languages = ['as']

    for language in languages:
        # global_csv_path = os.path.join(global_bigrams_parent, f'{language}/bigram.csv')
        global_csv_path = '/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_texts/ngrams_dictionary/hi/bigram_1000.csv'

        # recording_csv_path = os.path.join(recording_bigrams_parent, f'{language}/bigram.csv')
        recording_csv_path = '/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_texts/final/ngram_diff/as/bigram_diff.csv'

        target_lang_folder = os.path.join(target_parent_folder, language)
        os.makedirs(target_lang_folder, exist_ok= True)
        target_file = os.path.join(target_lang_folder, 'bigram_diff.csv')
        find_diff(global_csv_path, recording_csv_path, target_file)



