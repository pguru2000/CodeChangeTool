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
    for section in section_list:
        name_area = re.findall('<name>[^*]*?<\/name>', section)[0]
        section_name = name_area.replace('<name>', '').replace('</name>', '').strip()
        section_content = section.replace(name_area, '').replace('<section>', '').replace('</section>', '').strip()

        para_list = section_content.split('\n\n')

        no += 1

        arr = {
            'no': no,
            'section_name': section_name,
            'permutation_mode': permutation_mode,
            "section_visibility": False,
            'type': 'section',
            "number_of_elements": len(para_list),
            "rand_from": len(para_list),
            "rand_to": len(para_list),
            "content": section_content,
            "content_array": para_list,
            "element_type": "paragraphs"
        }
        arr_data.append(arr)
        for para in para_list:

            ele_list = para.split('\n')

            no += 1
            arr = {
                'no': no,
                'section_name': section_name,
                'permutation_mode': permutation_mode,
                "section_visibility": False,
                'type': 'paragraphs',
                "number_of_elements": len(ele_list),
                "rand_from": len(ele_list),
                "rand_to": len(ele_list),
                "content": para,
                "content_array": ele_list,
                "element_type": "elements"
            }
            arr_data.append(arr)
    return arr_data

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