import nltk.data
import re
import random
from random import randint



# text = 'Marseille 2e Arrondissement'
# sss = 'dans le Xème arrondissement de (Marseille|Lyon|Paris)'

# CITY_LIST = ['Marseille', 'Lyon', 'Paris']
# for city_name in CITY_LIST:
#     per_texts = re.findall(f'{city_name} [0-9]+e Arrondissement', text)
#     for per_text in per_texts:
#         number = per_text.split()[1].replace('e', '')
#         new_text = f'dans le {number}ème arrondissement de ' + city_name
#         print(new_text)
def replacePattern(src, dst, origtext):
    src_strip = src.strip()
    dst_strip = dst.strip()

    if ("'" not in src_strip and " " not in src_strip) or ("'" not in dst_strip and " " not in dst_strip):
        origtext = origtext.replace(src, dst)
    else:
        src_leading_spaces = len(src) - len(src.lstrip())
        src_ending_spaces = len(src) - len(src.rstrip())

        src_quote_split = src_strip.split("'")
        src_space_split = src_strip.split(" ")

        if len(src_quote_split[0]) < len(src_space_split[0]):            
            src_first_pattern = src_leading_spaces * " " + src_quote_split[0] + "'"
            src_second_pattern = "'".join(src_quote_split[1:]) + src_ending_spaces * " "
        else:
            src_first_pattern = src_leading_spaces * " " + src_space_split[0] + " "
            src_second_pattern = " ".join(src_space_split[1:]) + src_ending_spaces * " "

        dst_leading_spaces = len(dst) - len(dst.lstrip())
        dst_ending_spaces = len(dst) - len(dst.rstrip())

        dst_quote_split = dst_strip.split("'")
        dst_space_split = dst_strip.split(" ")

        if len(dst_quote_split[0]) < len(dst_space_split[0]):            
            dst_first_pattern = dst_leading_spaces * " " + dst_quote_split[0] + "'"
            dst_second_pattern = "'".join(dst_quote_split[1:]) + dst_ending_spaces * " "
        else:
            dst_first_pattern = dst_leading_spaces * " " + dst_space_split[0] + " "
            dst_second_pattern = " ".join(dst_space_split[1:]) + dst_ending_spaces * " "


        
        src_patterns = re.findall(src_first_pattern + '<[^*^>^<]*?>' + src_second_pattern, origtext)
        
        for src_pattern in src_patterns:
            html = src_pattern.replace(src_first_pattern, "", 1)
            html = html.split(">")[0] + ">"            

            origtext = origtext.replace(src_pattern, dst_first_pattern + html + dst_second_pattern)


        origtext = origtext.replace(src, dst)

    return origtext

rule = {
    "src": "effectuer reparer",
    "dest": "111"

}
origtext = "effectuer reparer"
origtext = replacePattern(rule['src'], rule['dest'], origtext)


print(origtext)




