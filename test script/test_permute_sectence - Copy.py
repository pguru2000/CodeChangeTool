import nltk.data
import re
import random
from random import randint

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
fp = open("permute_sentence_data/2.txt")
text = fp.read()

per_texts = re.findall('<permute-sentences-[0-9]+-[0-9]+>[^*]*?</permute-sentences-[0-9]+-[0-9]+>', text)
for per_text in per_texts:
    sentences_list = []
    result_list = []
    rand_from = per_text.split('>')[0].split('-')[-2]
    rand_to = per_text.split('>')[0].split('-')[-1]

    start_tag = '<permute-sentences-' + rand_from + '-' + rand_to + '>'
    end_tag = '</permute-sentences-' + rand_from + '-' + rand_to + '>'

    raw_text = per_text.replace(start_tag, '').replace(end_tag, '')    

    together_eles = re.findall('<together>[^*]*?</together>', raw_text)

    for together_ele in together_eles:
        together_sentence = together_ele.replace('<together>', '').replace('</together>', '')
        sentences_list.append(together_sentence)
        raw_text = raw_text.replace(together_ele, '')

    sentence_eles = tokenizer.tokenize(raw_text)
    for sentence_ele in sentence_eles:
        sentences_list.append(sentence_ele)

    count_array = len(sentences_list)
    rand_from = int(rand_from)
    rand_to = int(rand_to)
    if rand_from > count_array:
        rand_from = count_array
    if rand_to > count_array:
        rand_to = count_array

    n = randint(rand_from, rand_to)

    result_list = random.sample(sentences_list, n)
    result_text = ' '.join(result_list)

    text = text.replace(per_text, result_text)





#########################################################

per_texts = re.findall('<permute-sentences>[^*]*?</permute-sentences>', text)


for per_text in per_texts:
    sentences_list = []
    result_list = []
    raw_text = per_text.replace('<permute-sentences>', '').replace('</permute-sentences>', '')
    together_eles = re.findall('<together>[^*]*?</together>', raw_text)
    for together_ele in together_eles:
        together_sentence = together_ele.replace('<together>', '').replace('</together>', '')
        sentences_list.append(together_sentence)
        raw_text = raw_text.replace(together_ele, '')

    sentence_eles = tokenizer.tokenize(raw_text)
    for sentence_ele in sentence_eles:
    	sentences_list.append(sentence_ele)

    result_list = random.sample(sentences_list, len(sentences_list))
    result_text = ' '.join(result_list)

    text = text.replace(per_text, result_text)

print(text)