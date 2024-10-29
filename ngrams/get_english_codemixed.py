import re
import pandas as pd

def clean_text(sentence):
  sentence = re.sub(r'\s+', ' ', sentence)
  sentence = sentence.replace('] ,', '], ')
  sentence = sentence.replace(' ,', ', ')
  sentence = re.sub(r'(")\1+', r'\1', sentence)
  sentence = sentence.strip('"')
  sentence = sentence.replace('"', "'")
  sentence = re.sub(r'\s+', ' ', sentence)
  return sentence

discarded = ['TV', 'baby', 'baby_crying', 'baby_talking', 'barking', 'beep', 'bell', 'bird_squawk', 'breathing', 'buzz', 'buzzer', 'child', 'child_crying', 'child_laughing', 'child_talking', 'child_whining', 'child_yelling', 'children', 'children_talking', 'children_yelling', 'chiming', 'clanging', 'clanking', 'click', 'clicking', 'clink', 'clinking', 'cough', 'dishes', 'door', 'footsteps', 'gasp', 'groan', 'hiss', 'hmm', 'horn', 'hum', 'inhaling', 'laughter', 'meow', 'motorcycle', 'music', 'noise', 'nose_blowing', 'phone_ringing', 'phone_vibrating', 'popping', 'pounding', 'printer', 'rattling', 'ringing', 'rustling', 'scratching', 'screeching', 'sigh', 'singing', 'siren', 'smack', 'sneezing', 'sniffing', 'snorting', 'squawking', 'squeak', 'stammers', 'static', 'swallowing', 'talking', 'tapping', 'throat_clearing', 'thumping', 'tone', 'tones', 'trill', 'tsk', 'typewriter', 'ugh','uhh','uh-huh','umm', 'unintelligible', 'wheezing', 'whispering', 'whistling', 'yawning', 'yelling']

def remove_words(sentence):
    for word in discarded:
        pattern = re.compile(r'\[' + re.escape(word) + r'\]')
        sentence = re.sub(pattern, '', sentence)
        sentence = re.sub(r'\s+', ' ', sentence)
    return sentence


def remove_bracket_words(text):
    if '[' and ']' in text:
       pattern = re.compile(r'\[[^\]\[]+\]')
       text = re.sub(pattern, ' ', text)
       text = re.sub(r'\s+', ' ', text)
    return text

def keep_bracket_words(sentence):
    sentence = sentence.replace('[', ' [')
    sentence = sentence.replace(']', '] ')
    pattern = re.compile(r'\[([^\]]+)\]')
    matches = pattern.findall(sentence)
    for match in matches:
        words_inside_brackets = match.split()
        num_words_inside_brackets = len(words_inside_brackets)
        sentence = re.sub(rf'\b(\S+\s+){{0,{num_words_inside_brackets}}}\[{re.escape(match)}\]\s*', match + ' ', sentence)
    return sentence.strip()

data_path = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngram/scripts/sanskrit_sentences.txt'
with open(data_path, encoding='utf-8') as f:
    data = f.read()
    
sentences = data.split('\n')
sentences = [sentence for sentence in sentences if sentence.strip()]
sentence_count = len(sentences)
print(f'Sentence Count: {sentence_count}')
processed_sentences_1 = []
processed_sentences_2 = []
for sentence in sentences:
    sentence = remove_words(sentence)
    sentence_1 = remove_bracket_words(sentence)
    sentence_2 = keep_bracket_words(sentence)
    sentence_1 = clean_text(sentence_1)
    sentence_2 = clean_text(sentence_2)
    processed_sentences_1.append(sentence_1.strip())
    processed_sentences_2.append(sentence_2.strip())

if len(processed_sentences_1)==sentence_count and len(processed_sentences_1)==sentence_count:
  print('The original length matches')
else:
  print('The original length does not match')

output_file_1 = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngram/scripts/sanskrit_sentences-non-english.txt' #path needs to be changed
output_file_2 = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngram/scripts/sanskrit_sentences-eng.txt' #path needs to be changed

pd.DataFrame(processed_sentences_1).to_csv(output_file_1, mode='w', sep='\n', index=False, header=None)
pd.DataFrame(processed_sentences_2).to_csv(output_file_2, mode='w', sep='\n', index=False, header=None)
print(f'Files have been saved in the following locations: \n1) {output_file_1}\n2) {output_file_2}')