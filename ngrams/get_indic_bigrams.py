import pandas as pd
import os
import string

data_path = '/nlsasfs/home/ai4bharat/praveens/ttsteam/datasets/indic_clean_texts_2/indic-tts'

languages = [
    'Assamese', 'Bengali', 'Bodo', 'Dogri', 'Gujarati', 'Hindi', 'Kannada', 
    'Kashmiri', 'Konkani', 'Maithili', 'Malayalam', 'Manipuri', 'Marathi', 
    'Nepali', 'Odia', 'Punjabi', 'Sanskrit', 'Santali', 'Sindhi', 'Tamil', 
    'Telugu', 'Urdu'
]

def sent2bigrams(sentence):
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))
    words = sentence.split()
    return list([word[i:i+2] for word in words for i in range(len(word)-1)])

all_bigrams = []
for language in tqdm(languages):
    train = read_jsonl(f'{language}/metadata_train.json')
    train = pd.DataFrame.from_records(train)
    test = read_jsonl(f'{language}/metadata_test.json')
    test = pd.DataFrame.from_records(test)

    df = pd.concat([train, test])
    lang_bigrams = []
    for idx, row in df.iterrows():
        lang_bigrams.extend(sent2bigrams(line.strip()))
    bigrams = set(lang_bigrams)
    all_bigrams.append((language, len(bigrams)))

pd.DataFrame(all_bigrams, columns=['language', 'bigram_count']).to_csv('/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/Music-Source-Separation-Training/indicvoices_manifest/ivr_manifest_benchmark_splits/all_bigrams.csv', index=False)
    
        