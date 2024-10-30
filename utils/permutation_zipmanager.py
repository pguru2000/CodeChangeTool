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
from utils.permutation_txtmanager import extract_paragraphs
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

def replaceonefile(sf, output_format, addptag):
    global permutationruleList
    global nomatchtxtList


    # get the destination file name
    dest_filename = sf
    sfp = open('uploads/origfiles/' + sf)
    dfp = open('uploads/destfiles/' + dest_filename, "w")

    origtext = sfp.read()    

    # to remove ghost character(not showing but dot in special editor)
    # origtext = (origtext.encode('ascii', 'ignore')).decode("utf-8")

    result = EC.OK

    para_list = extract_paragraphs('uploads/origfiles/' + sf)

    if len(permutationruleList) != len(para_list):
        nomatchtxtList.append(sf)
        result = EC.ParagraphsNotSame
        return result

    else:
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

            result_content = perform_permute(content_array, permutation_mode, rand_from, rand_to, type)
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

    # remove ghost character
    # origtext = origtext.replace('﻿', '')


    # add p tag if the option is available
    if addptag == True and (output_format == '1' or output_format == '4'):
        origtext = add_ptag(origtext)

    # if putput is to strip json tags
    elif output_format == '3':
        origtext = strip_jsontags(origtext, addptag)

    #seterrorstring(geterrorstring() + "+++++++++++ processing " + sf + " file end+++++++++++\n\n")
    dfp.write(origtext.strip())
    sfp.close()
    dfp.close()
    return result

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

def strip_jsontags(origtext, addptag):
    items = re.findall('#start-[^*]*?#end-', origtext)

    for item in items:
        para_id = item.split('#')[1].replace('start-', '')
        para_content = item.split('#start-' + para_id + '#')[1].replace('#end-', '').strip()

        old_str = item + para_id + '#'

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
        origtext = origtext.replace(old_str, para_content)
    return origtext

def perform_permute(content_array, permutation_mode, rand_from, rand_to, type):

    if type == 'section':
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
            combinations = itertools.combinations(content_array, n)
            result_array = random.choice(list(combinations))

        elif permutation_mode == 'ALL_PERMUTABLE':
            result_array = random.sample(content_array, n)

        elif permutation_mode == 'ALL_PERMUTABLE_EXCEPT_FIRST':

            result_array.append(first_element)
            if n > 1:
                tmp_array = random.sample(content_array[1:], n-1)
                for ele in tmp_array:
                    result_array.append(ele)

        elif permutation_mode == 'ALL_PERMUTABLE_EXCEPT_LAST':

            if n > 1:
                tmp_array = random.sample(content_array[:-1], n-1)
                for ele in tmp_array:
                    result_array.append(ele)
            result_array.append(last_element)

        elif permutation_mode == 'ALL_PERMUTABLE_EXCEPT_FIRST_LAST':

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
            return '\n'.join(result_array)
        else:
            return '\n'.join(content_array)


def loadPermutationRule(project_name):
    global permutationruleList
    #datas = CL.objects.all()
    datas = PP.objects.raw(""
                           "SELECT "
                           "    * "                           
                           "FROM "
                           "    managetemplate_permutationparagraphs "
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

def createTxt(src_path, dest_path, result_file_name, addptag):
    data = []

    dash = '\n----------\n'
    text_list = []
    for file_title in os.listdir(src_path):
        if file_title.endswith('.txt'):
            file_path = os.path.join(src_path, file_title)
            sfp = open(file_path)
            origtext = sfp.read().strip()
            text_list.append(origtext)
    totaltext = dash.join(text_list)

    file_path = os.path.join(dest_path, result_file_name)
    with open(file_path, 'w') as f:
        f.write(totaltext)
        f.close()

def replacevariables(zipfile, output_format, addptag, project_name):
    global nomatchtxtList

    print('=================  permutation is placed')

    if unzip(zipfile, 'uploads/origfiles') == False:
        return EC.UnZipFail

    result = EC.OK

    nomatchtxtList = []

    origfiles = [f for f in listdir('uploads/origfiles') if isfile(join('uploads/origfiles', f))]

    loadPermutationRule(project_name)

    # first replace all files
    for i in range(len(origfiles)):
        sf = origfiles[i]
        if sf[-4:] != ".txt":
            return EC.InvalidTxt

        res = replaceonefile(sf, output_format, addptag)

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
    # if jsonoutput == True:
    #
    #     result_file_name = "resultat-permutation-" + '{:02d}'.format(now.day) + "-" + '{:02d}'.format(now.month) + "-" + str(
    #         now.year) + "-" + '{:02d}'.format(now.hour) + "h" + '{:02d}'.format(now.minute) + ".json"
    #     createJson('uploads/destfiles', 'static/result', result_file_name, addptag)
    #     file_root = "static/result/" + result_file_name
    # else:
    #     result_file_name = "resultat-permutation-" + '{:02d}'.format(now.day) + "-" + '{:02d}'.format(now.month) + "-" + str(now.year) + "-" + '{:02d}'.format(now.hour) + "h" + '{:02d}'.format(now.minute) + ".zip"
    #     #file_root = "static/" + result_file_name
    #     file_root = "static/result/" + result_file_name
    #     zip('uploads/destfiles', file_root)

    # if output format is a zip with all texts
    if output_format == '1' or output_format == '3':
        result_file_name = "resultat-permutation-" + '{:02d}'.format(now.day) + "-" + '{:02d}'.format(
            now.month) + "-" + str(now.year) + "-" + '{:02d}'.format(now.hour) + "h" + '{:02d}'.format(
            now.minute) + ".zip"
        # file_root = "static/" + result_file_name
        file_root = "static/result/" + result_file_name
        zip('uploads/destfiles', file_root)

    # if output format is json output
    elif output_format == '2':
        result_file_name = "resultat-permutation-" + '{:02d}'.format(now.day) + "-" + '{:02d}'.format(
            now.month) + "-" + str(
            now.year) + "-" + '{:02d}'.format(now.hour) + "h" + '{:02d}'.format(now.minute) + ".json"
        createJson('uploads/destfiles', 'static/result', result_file_name, addptag)
        file_root = "static/result/" + result_file_name

    # if output format is to gather all texts in 1 txt
    elif output_format == '4':
        result_file_name = "resultat-permutation-" + '{:02d}'.format(now.day) + "-" + '{:02d}'.format(
            now.month) + "-" + str(
            now.year) + "-" + '{:02d}'.format(now.hour) + "h" + '{:02d}'.format(now.minute) + ".txt"
        createTxt('uploads/destfiles', 'static/result', result_file_name, addptag)
        file_root = "static/result/" + result_file_name

    set_download_root(file_root)

    return result
