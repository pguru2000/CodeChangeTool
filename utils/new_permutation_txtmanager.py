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
from os import listdir
from os.path import isfile, join
import re
import os
import random
from random import randint
import string
import sys
import pytz
sys.setrecursionlimit(10000)
from managetemplate.models import ConversionRule as CR
from managetemplate.models import Condition as CL
from managetemplate.models import VariableCondition as VARCD


notexistvariables = []
novaluefiles = []
noconditions = []
cvrule = []
conditionList = {}
varconditionList = {}


def extract_paragraphs(filename):
    sfp = open(filename)
    origtext = sfp.read()
    section_list = re.findall('<section>[^*]*?<\/section>', origtext)

    arr_data = []
    permutation_mode = 'ALL_NOT_PERMUTABLE'
    no = 0

    first_normal_para_indexed = True
    normal_sections_list = []
    for section in section_list:
        name_area = re.findall('<name>[^*]*?<\/name>', section)[0]
        section_name = name_area.replace('<name>', '').replace('</name>', '').strip()
        section_content = section.replace(name_area, '').replace('<section>', '').replace('</section>', '').strip()

        para_list = section_content.split('\n\n')

        no += 1

        if section_name == 'META-TITLE':
            para_type = 'META_TITLE'
        elif section_name == 'META-DESCRIPTION':
            para_type = 'META_DESCRIPTION'
        elif section_name == 'H1':
            para_type = 'H1_TITLE'
        elif section_name == 'INTRODUCTION':
            para_type = 'INTRO_PARAGRAPH'
        elif section_name == 'CONCLUSION':
            para_type = 'CONCLUSION_PARAGRAPH'
        else:
            para_type = 'NORMAL_PARAGRAPH'
            normal_sections_list.append(section)


        arr = {
            'no': no,
            'section_name': section_name,
            'permutation_mode': permutation_mode,
            "section_visibility": False,
            'type': 'section',
            "number_of_elements": len(para_list),
            'para_type': para_type,
            "rand_from": len(para_list),
            "rand_to": len(para_list),
            "content": section_content,
            "content_array": para_list,
            "element_type": "paragraphs",
            "first_normal_para": False
        }
        arr_data.append(arr)
        for para in para_list:
            first_normal_para = False

            ele_list = para.split('\n')
            rand_from = len(ele_list)
            rand_to = len(ele_list)

            hn_title = hn_title_detect(para)

            if hn_title == True:
                para_type = 'Hn_TITLE'
                rand_from = 1
                rand_to = 1
            elif para.startswith('<intro>') and para.endswith('</intro>'):
                para_type = 'INTRO_PARAGRAPH'
            elif para.startswith('<conclusion>') and para.endswith('</conclusion>'):
                para_type = 'CONCLUSION_PARAGRAPH'
            else:
                para_type = 'NORMAL_PARAGRAPH'

            if para_type == 'NORMAL_PARAGRAPH' and first_normal_para_indexed == True:
                first_normal_para = True
                first_normal_para_indexed = False
            no += 1
            arr = {
                'no': no,
                'section_name': section_name,
                'permutation_mode': permutation_mode,
                "section_visibility": False,
                'type': 'paragraphs',
                "number_of_elements": len(ele_list),
                'para_type': para_type,
                "rand_from": rand_from,
                "rand_to": rand_to,
                "content": para,
                "content_array": ele_list,
                "element_type": "elements",
                "first_normal_para": first_normal_para
            }
            arr_data.append(arr)

    normal_sections = {
        "permute_sections": False,
        "permutation_mode": permutation_mode,
        'texts': '\n\n'.join(normal_sections_list),
        'count': len(normal_sections_list),
        "rand_from": len(normal_sections_list),
        "rand_to": len(normal_sections_list),
        "list_of_sections": normal_sections_list
    }
    return arr_data, normal_sections

def extract_sections(filename):
    sfp = open(filename)
    origtext = sfp.read()
    
    section_list = re.findall('#start-section[^*]*?#end-section', origtext)
    
    normal_sections_list = []
    for section in section_list:

        section_id = section.split('#')[1].replace('start-section', '')
        section_content = section + section_id + '#'
        normal_sections_list.append(section_content)

    return normal_sections_list

def get_min_max_words_of_paragraph(content, rand_from, rand_to):
    rand_from = int(rand_from)
    rand_to = int(rand_to)
    ele_list = content.split('\n')
    words_of_elements = []
    for ele in ele_list:
        ele = ele.strip()
        if ele == '':
            continue
        words_of_elements.append(len(ele.split()))
    words_of_elements = sorted(words_of_elements)
    if rand_from < 1:
        min_words = 0
    else:
        min_words = sum(words_of_elements[:rand_from])
    max_words = sum(words_of_elements[len(words_of_elements) - rand_to:])

    return min_words, max_words

def get_min_max_words_of_section(rand_from, rand_to, min_words_list, max_words_list):
    min_words_list = sorted(min_words_list)
    max_words_list = sorted(max_words_list)
    rand_from = int(rand_from)
    rand_to = int(rand_to)
    min_words = sum(min_words_list[:rand_from])
    max_words = sum(max_words_list[len(max_words_list) - rand_to:])

    return min_words, max_words

def hn_title_detect(content):
    re_texts = re.findall('<h[1-9]>[^*]*?</h[1-9]>', content)
    count_hn = len(re_texts)
    ele_list = content.split('\n')
    if count_hn > 0 and count_hn == len(ele_list):
        return True
    else:
        return False
