import zipfile
import json
from datetime import datetime
from utils.xlsmanager import getconvmap
from utils.xlsmanager import getvariables
from utils.errorcode import ErrorCode as EC
from utils.errorcode import geterrorstring
from utils.errorcode import seterrorstring
from utils.download_root import set_download_root
from utils.download_root import get_download_root
from utils.new_permutation_txtmanager import extract_paragraphs
from utils.new_permutation_txtmanager import extract_sections
from os import listdir
from os.path import isfile, join
import re
import os
import random
from random import randint
import itertools
import string
import sys
import pytz
import nltk.data
sys.setrecursionlimit(10000)
from managetemplate.models import ConversionRule as CR
from managetemplate.models import Condition as CL
from managetemplate.models import VariableCondition as VARCD
from managetemplate.models import PermutationParagraphs as PP

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')


nomatchtxtList = []
permutationruleList = []
sectionpermutationrule = {}



def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def unzip(path, destfolder):
    zip = zipfile.ZipFile(path)
    zip.extractall(destfolder)
    zip.close()
    pass


def zip(path, destname):
    ziper = zipfile.ZipFile(destname, mode = 'w', compression=zipfile.ZIP_DEFLATED)
    origfiles = [f for f in listdir(path) if isfile(join(path, f))]
    for i in range(len(origfiles)):
        #ziper.write(join(path, origfiles[i]), "result/" + origfiles[i], zipfile.ZIP_DEFLATED)
        ziper.write(join(path, origfiles[i]), origfiles[i], zipfile.ZIP_DEFLATED)
    ziper.close()
    pass


def iszipfile(file_name):
    return zipfile.is_zipfile(file_name)

def permute_sentences(text):
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

    return text

def replaceonefile(sf, jsonoutput, addptag):
    print('replace one file')
    global permutationruleList
    global sectionpermutationrule
    global nomatchtxtList

    # get the destination file name
    dest_filename = sf
    sfp = open('uploads/origfiles/' + sf)
    dfp = open('uploads/destfiles/' + dest_filename, "w")

    origtext = sfp.read()
    

    # to remove ghost character(not showing but dot in special editor)
    # origtext = (origtext.encode('ascii', 'ignore')).decode("utf-8")

    result = EC.OK

    para_list, normal_sections = extract_paragraphs('uploads/origfiles/' + sf)



    if len(permutationruleList) != len(para_list):
        nomatchtxtList.append(sf)
        result = EC.ParagraphsNotSame
        return result
    
    if sectionpermutationrule['permute_sections'] == True:

        list_of_sections = normal_sections['list_of_sections']
        permutation_mode_section = sectionpermutationrule['permutation_mode_section']
        sections_rand_from = sectionpermutationrule['sections_rand_from']
        sections_rand_to = sectionpermutationrule['sections_rand_to']

        # 2022 02 22 permute section for #start-section1#

        new_list_of_sections = extract_sections('uploads/origfiles/' + sf)
        permuted_sections = perform_permute(new_list_of_sections, permutation_mode_section, sections_rand_from, sections_rand_to, 'section', sectionpermutationrule["not_permute_conditional_sections"])
        origtext = origtext.replace('\n\n'.join(new_list_of_sections), permuted_sections)

        #### origin code ###
        ###   permuted_sections = perform_permute(list_of_sections, permutation_mode_section, sections_rand_from, sections_rand_to, 'section')
        ###   origtext = origtext.replace(normal_sections['texts'], permuted_sections)
        #### origin code ###

    origtext = remove_duplicated_intro_conclu_sections(origtext, para_list)

    for i in range(len(permutationruleList)):
        para_from_db = permutationruleList[i]
        para_from_txt = para_list[i]

        permutation_mode = para_from_db['permutation_mode']
        rand_from = para_from_db['rand_from']
        rand_to = para_from_db['rand_to']
        type = para_from_db['type']
        section_visibility = para_from_db['section_visibility']

        content = para_from_txt['content']
        content_array = para_from_txt['content_array']

        if content in origtext:
            result_content = perform_permute(content_array, permutation_mode, rand_from, rand_to, type,  False)
            origtext = origtext.replace(content, result_content)

        if type == 'section' and section_visibility == False:
            origtext = origtext.replace('<name>' + para_from_db['section_name'] + '</name>', '')
        elif type == 'section' and section_visibility == True:
            origtext = origtext.replace('<name>' + para_from_db['section_name'] + '</name>', '\n\n' + para_from_db['section_name'] + '\n\n')

    # remove SECTION NAME tags
    origtext = origtext.replace('<section>', '').replace('</section>', '').replace('<name>', '').replace('</name>', '')
    origtext = permute_sentences(origtext)


    # merge multi blank lines into 1
    origtext = re.sub(r'(\n\s*)+\n+', '\n\n', origtext)

    # [sme] function at 2022 10 25
    origtext = perform_smeTag(origtext)

    # remove ghost character
    # origtext = origtext.replace('﻿', '')

    # add p tag if it is set.
    if addptag and jsonoutput == False:
        origtext = add_ptag(origtext)

    #seterrorstring(geterrorstring() + "+++++++++++ processing " + sf + " file end+++++++++++\n\n")
    dfp.write(origtext.strip())
    sfp.close()
    dfp.close()
    return result

def perform_smeTag(origtext):
    lines = origtext.split("\n")
    new_lines = []

    for line in lines:
        sentences = line.split(" ")
        new_sentences = []
        for s_index, sentence in enumerate(sentences):
            if sentence.startswith("[s]") and s_index != 0:
                continue
            elif sentence.startswith("[m]") and ( s_index == 0 or s_index == (len(sentences) - 1) ) :
                continue
            elif sentence.startswith("[e]") and s_index != (len(sentences) - 1):
                continue
            elif sentence.startswith("[sm]") and s_index == (len(sentences) - 1):
                continue
            elif sentence.startswith("[me]") and s_index == 0:
                continue
            else:
                new_sentence = sentence.replace("[s]", "")
                new_sentence = new_sentence.replace("[m]", "")
                new_sentence = new_sentence.replace("[e]", "")
                new_sentence = new_sentence.replace("[sm]", "")
                new_sentence = new_sentence.replace("[me]", "")

                new_sentence = new_sentence.replace("[/s]", "")
                new_sentence = new_sentence.replace("[/m]", "")
                new_sentence = new_sentence.replace("[/e]", "")
                new_sentence = new_sentence.replace("[/sm]", "")
                new_sentence = new_sentence.replace("[/me]", "")

                new_sentences.append(new_sentence)

        new_lines.append(" ".join(new_sentences))
    return "\n".join(new_lines)

def add_ptag(origtext):

    lines = origtext.split('\n\n')
    if len(lines) > 1:
        new_content = ''
        for line in lines:
            line = line.strip()
            if line.startswith('META TITLE :') or line.startswith('META DESCRIPTION :') or line.startswith(
                    '<h') or line.startswith('<p>') or line.startswith('TITRE') or line.isupper():
                new_line = line + '\n\n'
            else:
                new_line = '<p>' + line + '</p>' + '\n\n'
            new_content += new_line
        origtext = new_content.strip()
    return origtext

def remove_duplicated_intro_conclu_sections(origtext, para_list):
    list_of_intro_section = []
    list_of_conclu_section = []

    list_of_intro_paragraph = {}
    list_of_conclu_paragraph = {}
    for para in para_list:
        if para['type'] == 'section':
            list_of_intro_paragraph[para['section_name']] = []
            list_of_conclu_paragraph[para['section_name']] = []
        if para['type'] == 'section' and para['para_type'] == 'INTRODUCTION_PARAGRAPH':
            list_of_intro_section.append(para)
        elif para['type'] == 'section' and para['para_type'] == 'CONCLUSION_PARAGRAPH':
            list_of_conclu_section.append(para)
        elif para['type'] == 'paragraph' and para['para_type'] == 'INTRODUCTION_PARAGRAPH':
            list_of_intro_paragraph[para['section_name']].append(para)
        elif para['type'] == 'paragraph' and para['para_type'] == 'CONCLUSION_PARAGRAPH':
            list_of_conclu_paragraph[para['section_name']].append(para)

    if len(list_of_intro_section) > 1:
        list_of_remove_intro_section = random.sample(list_of_intro_section, len(list_of_intro_section) - 1)
        for item in list_of_remove_intro_section:
            origtext = origtext.replace(item, '')
    if len(list_of_conclu_section) > 1:
        list_of_remove_conclu_section = random.sample(list_of_conclu_section, len(list_of_conclu_section) - 1)
        for item in list_of_remove_conclu_section:
            origtext = origtext.replace(item, '')

    for k, intro_list in list_of_intro_paragraph.items():
        if len(intro_list) > 1:
            list_of_remove_intro = random.sample(intro_list, len(intro_list) - 1)
            for item in list_of_remove_intro:
                origtext = origtext.replace(item, '')

    for k, conclu_list in list_of_conclu_paragraph.items():
        if len(conclu_list) > 1:
            list_of_remove_conclu=random.sample(conclu_list, len(conclu_list) - 1)
            for item in list_of_remove_conclu:
                origtext = origtext.replace(item, '')

    return origtext

# def perform_permute(content_array, permutation_mode, rand_from, rand_to, type):
#     count_array = len(content_array)
#     if rand_from > count_array:
#         rand_from = count_array
#     if rand_to > count_array:
#         rand_to = count_array

#     n = randint(rand_from, rand_to)

#     first_element = content_array[0]
#     last_element = content_array[count_array - 1]

#     result_array = []

#     if permutation_mode == 'ALL_NOT_PERMUTABLE':
#         combinations = itertools.combinations(content_array, n)
#         result_array = random.choice(list(combinations))

#     elif permutation_mode == 'ALL_PERMUTABLE':
#         result_array = random.sample(content_array, n)

#     elif permutation_mode == 'ALL_PERMUTABLE_EXCEPT_FIRST':

#         result_array.append(first_element)
#         if n > 1:
#             tmp_array = random.sample(content_array[1:], n-1)
#             for ele in tmp_array:
#                 result_array.append(ele)

#     elif permutation_mode == 'ALL_PERMUTABLE_EXCEPT_LAST':

#         if n > 1:
#             tmp_array = random.sample(content_array[:-1], n-1)
#             for ele in tmp_array:
#                 result_array.append(ele)
#         result_array.append(last_element)

#     elif permutation_mode == 'ALL_PERMUTABLE_EXCEPT_FIRST_LAST':

#         if n == 1:
#             result_array.append(first_element)
#         elif n == 2:
#             result_array.append(first_element)
#             result_array.append(last_element)
#         elif n > 2:
#             result_array.append(first_element)
#             tmp_array = random.sample(content_array[1:-1], n - 2)
#             for ele in tmp_array:
#                 result_array.append(ele)
#             result_array.append(last_element)

#     if type == 'section':
#         return '\n\n'.join(result_array)
#     else:
#         return ' '.join(result_array)
def perform_permute(content_array, permutation_mode, rand_from, rand_to, type, not_permute_conditional_sections):

    if type == 'section':
        cond_sections = []
        cond_index_list = []
        ordi_sections = []
        ordi_index_list = []
        if not_permute_conditional_sections == True:
            for index, section_str in enumerate( content_array ):
                section_content = "\n".join(section_str.split("\n")[1:-1]).strip()
                if section_content.startswith("<cond-"):
                    cond_id = section_content.split(">")[0].replace("<cond-", "")
                    if section_content.endswith("</cond-" + cond_id + ">"):
                        cond_sections.append(section_str)
                        cond_index_list.append(index)
                    else:
                        ordi_sections.append(section_str)
                        ordi_index_list.append(index)
                else:
                    ordi_sections.append(section_str)
                    ordi_index_list.append(index)
        
        count_array = len(content_array)
        if rand_from > count_array:
            rand_from = count_array
        if rand_to > count_array:
            rand_to = count_array

        n = randint(rand_from, rand_to)



        first_element = content_array[0]
        last_element = content_array[count_array - 1]

        result_array = []

        if permutation_mode == 'ALL_NOT_PERMUTABLE':
            if not_permute_conditional_sections == True:
                if len(cond_index_list) >= n:
                    index_list = cond_index_list[:n]
                else:
                    rand_ordi_index_list = random.sample(ordi_index_list, n - len(cond_index_list))
                    index_list = cond_index_list + rand_ordi_index_list
                    index_list.sort()

                for index in index_list:
                    result_array.append(content_array[index])

            else:
                combinations = itertools.combinations(content_array, n)
                result_array = random.choice(list(combinations))

        elif permutation_mode == 'ALL_PERMUTABLE':
            if not_permute_conditional_sections == True:
                if len(cond_index_list) >= n:
                    index_list = cond_index_list[:n]
                else:
                    rand_ordi_index_list = random.sample(ordi_index_list, n - len(cond_index_list))
                    index_list = cond_index_list + rand_ordi_index_list
                random.shuffle(index_list)

                for index in index_list:
                    result_array.append(content_array[index])

            else:
                result_array = random.sample(content_array, n)

        elif permutation_mode == 'ALL_PERMUTABLE_EXCEPT_FIRST':
            if not_permute_conditional_sections == True:
                if len(cond_index_list) >= n:
                    index_list = cond_index_list[:n]
                else:
                    if 0 in ordi_index_list:
                        rand_ordi_index_list = random.sample(ordi_index_list[1:], n - len(cond_index_list) - 1)
                        index_list = [0] + cond_index_list + rand_ordi_index_list
                    else:
                        rand_ordi_index_list = random.sample(ordi_index_list, n - len(cond_index_list))
                        index_list = cond_index_list + rand_ordi_index_list

                tail_index_list = index_list[1:]
                random.shuffle(tail_index_list)

                result_array.append(first_element)
                for index in tail_index_list:
                    result_array.append(content_array[index])
            else:
                result_array.append(first_element)
                if n > 1:
                    tmp_array = random.sample(content_array[1:], n-1)
                    for ele in tmp_array:
                        result_array.append(ele)

        elif permutation_mode == 'ALL_PERMUTABLE_EXCEPT_LAST':
            if not_permute_conditional_sections == True:
                if len(cond_index_list) >= n:
                    index_list = cond_index_list[-n:]
                else:
                    if (count_array - 1) in ordi_index_list:
                        rand_ordi_index_list = random.sample(ordi_index_list[:-1], n - len(cond_index_list) - 1)
                        index_list = cond_index_list + rand_ordi_index_list + [count_array - 1]
                    else:
                        rand_ordi_index_list = random.sample(ordi_index_list, n - len(cond_index_list))
                        index_list = rand_ordi_index_list + cond_index_list

                head_index_list = index_list[:-1]
                random.shuffle(head_index_list)

                for index in head_index_list:
                    result_array.append(content_array[index])
                result_array.append(last_element)
            else:

                if n > 1:
                    tmp_array = random.sample(content_array[:-1], n-1)
                    for ele in tmp_array:
                        result_array.append(ele)
                result_array.append(last_element)

        elif permutation_mode == 'ALL_PERMUTABLE_EXCEPT_FIRST_LAST':
            if not_permute_conditional_sections == True:
                if len(cond_index_list) >= n:
                    index_list = cond_index_list[:n]
                else:
                    if 0 in ordi_index_list and (count_array - 1) in ordi_index_list:
                        rand_ordi_index_list = random.sample(ordi_index_list[1:-1], n - len(cond_index_list) - 2)
                        index_list = [0] + cond_index_list + rand_ordi_index_list + [count_array - 1]

                    elif 0 in ordi_index_list:
                        rand_ordi_index_list = random.sample(ordi_index_list[1:], n - len(cond_index_list) - 1)
                        index_list = [0]  + rand_ordi_index_list + cond_index_list

                    elif (count_array - 1) in ordi_index_list:
                        rand_ordi_index_list = random.sample(ordi_index_list[:-1], n - len(cond_index_list) - 1)
                        index_list = cond_index_list  + rand_ordi_index_list + [count_array - 1]
                    else:
                        rand_ordi_index_list = random.sample(ordi_index_list, n - len(cond_index_list))
                        index_list = cond_index_list[:-1] + rand_ordi_index_list + cond_index_list[-1:]

                middle_index_list = index_list[1:-1]
                random.shuffle(middle_index_list)
                
                result_array.append(content_array[0])            
                for index in middle_index_list:
                    result_array.append(content_array[index])
                result_array.append(content_array[count_array - 1])
            else:

                if n == 1:
                    result_array.append(first_element)
                elif n == 2:
                    result_array.append(first_element)
                    result_array.append(last_element)
                elif n > 2:
                    result_array.append(first_element)
                    tmp_array = random.sample(content_array[1:-1], n - 2)
                    for ele in tmp_array:
                        result_array.append(ele)
                    result_array.append(last_element)
    
        return '\n\n'.join(result_array)
    else:
        title_element = ''
        keep_elements = []
        new_content_array = []
        
        if content_array[0].strip().startswith('<h'):
            title_element = content_array[0]

        for index, element in enumerate(content_array):
            if index == 0:
                if element.startswith('<h'):
                    title_element = content_array[0]
                else:
                    new_content_array.append(element)
                continue
           
            if element.startswith('<keep>'):
                ele_content = element.replace('<keep>', '').replace('</keep>', '')
                keep_elements.append(ele_content)
            else:
                new_content_array.append(element)

        diff_n = len(content_array) - len(new_content_array)

        count_array = len(content_array)
        if rand_from > count_array:
            rand_from = count_array
        if rand_to > count_array:
            rand_to = count_array

        n = randint(rand_from, rand_to)

        if n > diff_n:
            first_element = new_content_array[0]
            last_element = new_content_array[-1]

            result_array = []

            if permutation_mode == 'ALL_NOT_PERMUTABLE':
                combinations = itertools.combinations(new_content_array, n - diff_n)
                arr = list(random.choice(list(combinations)))
                if title_element != '':
                    arr.append(title_element)
                for keep_ele in keep_elements:
                    arr.append(keep_ele)

                for ele in content_array:
                    if ele in arr:
                        result_array.append(ele)

            elif permutation_mode == 'ALL_PERMUTABLE':
                arr = random.sample(new_content_array, n - diff_n)
                for keep_ele in keep_elements:
                    arr.append(keep_ele)
                result_array = random.sample(arr, len(arr))
                if title_element != '':
                    result_array.insert(0, title_element)

            elif permutation_mode == 'ALL_PERMUTABLE_EXCEPT_FIRST':               
                if (n - diff_n) > 1:
                    
                    tmp_array = random.sample(new_content_array[1:], n - diff_n -1)
                    for ele in tmp_array:
                        result_array.append(ele)

                    for keep_ele in keep_elements:
                        result_array.append(keep_ele)

                    result_array = random.sample(result_array, len(result_array))
                result_array.insert(0, first_element)
                if title_element != '':
                    result_array.insert(0, title_element)

            elif permutation_mode == 'ALL_PERMUTABLE_EXCEPT_LAST':

                if (n - diff_n) > 1:
                    tmp_array = random.sample(new_content_array[:-1], n - diff_n -1)
                    for ele in tmp_array:
                        result_array.append(ele)
                    for keep_ele in keep_elements:
                        result_array.append(keep_ele)

                    result_array = random.sample(result_array, len(result_array))
                result_array.append(last_element)
                if title_element != '':
                    result_array.insert(0, title_element)

            elif permutation_mode == 'ALL_PERMUTABLE_EXCEPT_FIRST_LAST':

                if n == 1:
                    result_array.append(first_element)
                elif n == 2:
                    result_array.append(first_element)
                    result_array.append(last_element)
                elif (n - diff_n) > 2:                    
                    tmp_array = random.sample(new_content_array[1:-1], n - diff_n - 2)
                    for ele in tmp_array:
                        result_array.append(ele)
                    for keep_ele in keep_elements:
                        result_array.append(keep_ele)
                    result_array = random.sample(result_array, len(result_array))

                    result_array.append(last_element)
                    result_array.insert(0, first_element)
                    if title_element != '':
                        result_array.insert(0, title_element)
            # return '\n'.join(result_array)
            resultTxt = ' '.join(result_array)
            resultTxt = resultTxt.strip()
            return resultTxt
        else:
            # return '\n'.join(content_array)
            resultTxt = ' '.join(content_array)
            resultTxt = resultTxt.strip()
            return resultTxt

def loadPermutationRule(project_name):
    global permutationruleList
    #datas = CL.objects.all()
    datas = PP.objects.raw(""
                           "SELECT "
                           "    * "                           
                           "FROM "
                           "    permutation_newpermutationparagraphs "
                           "WHERE "
                           "    project_name = '{}' ".format(project_name))
    datas = list(datas)
    permutationruleList = []
    for data in datas:
        item = {
            "section_name": data.section_name,
            "section_visibility": data.section_visibility,
            "permutation_mode": data.permutation_mode,
            "number_of_elements": data.number_of_elements,
            "type": data.type,
            "rand_to": data.rand_to,
            "rand_from": data.rand_from
        }
        permutationruleList.append(item)

def loadSectionPermutationRule(project_name):
    global sectionpermutationrule
    #datas = CL.objects.all()
    datas = PP.objects.raw(""
                           "SELECT "
                           "    * "                           
                           "FROM "
                           "    permutation_newpermutationgeneral "
                           "WHERE "
                           "    project_name = '{}' ".format(project_name))
    datas = list(datas)

    for data in datas:
        sectionpermutationrule = {
            "permute_sections": data.permute_sections,
            "permutation_mode_section": data.permutation_mode_section,
            "sections_rand_from": data.sections_rand_from,
            "sections_rand_to": data.sections_rand_to,
            "count_normalsections": data.count_normalsections,
            "not_permute_conditional_sections": data.not_permute_conditional_sections
        }

def createJson(src_path, dest_path, result_file_name, addptag):
    data = []
    for file_title in os.listdir(src_path):
        if file_title.endswith('.txt'):
            file_path = os.path.join(src_path, file_title)
            sfp = open(file_path, encoding='utf-8')
            origtext = sfp.read()

            items = re.findall('#start-[^*]*?#end-', origtext)
            dic = {}
            for item in items:
                para_id = item.split('#')[1].replace('start-', '')
                para_content = item.split('#start-' + para_id + '#')[1].replace('#end-', '').strip()

                if addptag == True:
                    paras = para_content.split('\n\n')
                    if len(paras) > 1 or 'section' in para_id or 'text' in para_id or 'paragraph' in para_id or 'intro' in para_id or 'conclusion' in para_id:
                        new_para_content = ''
                        for para in paras:
                            para = para.strip()
                            if para == '':
                                continue
                            new_para = '<p>' + para + '</p>' + '\n\n'
                            new_para_content += new_para
                        para_content = new_para_content.strip()

                dic[para_id] = para_content
            data.append(dic)
    file_path = os.path.join(dest_path, result_file_name)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
        f.close()
        # json_str = json.dumps(str(data))
        # f.write(json_str)

def replacevariables(zipfile, jsonoutput, addptag, project_name):
    global nomatchtxtList

    if unzip(zipfile, 'uploads/origfiles') == False:
        return EC.UnZipFail

    result = EC.OK

    nomatchtxtList = []

    origfiles = [f for f in listdir('uploads/origfiles') if isfile(join('uploads/origfiles', f))]

    loadPermutationRule(project_name)
    loadSectionPermutationRule(project_name)

    # first replace all files
    for i in range(len(origfiles)):
        sf = origfiles[i]
        if sf[-4:] != ".txt":
            return EC.InvalidTxt

        res = replaceonefile(sf, jsonoutput, addptag)

        if res != EC.OK:
            result = res

    if len(nomatchtxtList) > 0:
        errormsg = "There are {} text files which are not the same as the paragraph template:\n".format(len(nomatchtxtList))
        for i in range(len(nomatchtxtList)):
            errormsg = errormsg + nomatchtxtList[i] + "\n"
            if i >= 2:
                errormsg = errormsg + "...\n"
                break
        seterrorstring(geterrorstring() + errormsg)

    # last zip result files.
    tz_paris = pytz.timezone('Europe/Paris')
    now = datetime.now(tz_paris)
    if jsonoutput == True:

        result_file_name = "resultat-permutation-" + '{:02d}'.format(now.day) + "-" + '{:02d}'.format(now.month) + "-" + str(
            now.year) + "-" + '{:02d}'.format(now.hour) + "h" + '{:02d}'.format(now.minute) + ".json"
        createJson('uploads/destfiles', 'static/result', result_file_name, addptag)
        file_root = "static/result/" + result_file_name
    else:
        result_file_name = "resultat-permutation-" + '{:02d}'.format(now.day) + "-" + '{:02d}'.format(now.month) + "-" + str(now.year) + "-" + '{:02d}'.format(now.hour) + "h" + '{:02d}'.format(now.minute) + ".zip"
        #file_root = "static/" + result_file_name
        file_root = "static/result/" + result_file_name
        zip('uploads/destfiles', file_root)

    set_download_root(file_root)

    return result
