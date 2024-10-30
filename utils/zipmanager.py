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
import pathlib
sys.setrecursionlimit(10000)
from managetemplate.models import ConversionRule as CR
from managetemplate.models import Condition as CL
from managetemplate.models import VariableCondition as VARCD

from cluster.models import ClusterCondition as ClusterCondition


notexistvariables = []
novaluefiles = []
noconditions = []
cvrule = []
nopermutetags = []
nopairedtags = []
conditionList = {}
varconditionList = {}
clusterconditionList = {}


global check_process
check_process = 0


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

def filecount():
    file_count = 0
    for path in pathlib.Path('uploads/origfiles').iterdir():
        if path.is_file():
            file_count += 1
    return file_count


# def evalcore(condelem, idx):
#     if len(condelem) == 4:
#         vmap = getconvmap()
#         A = vmap[condelem[1]][idx]
#         B = condelem[3]
#         if condelem[2] == '<':
#             return A < B
#         elif condelem[2] == '=':
#             return A == B
#         elif condelem[2] == '<=':
#             return A <= B
#         elif condelem[2] == '>':
#             return A > B
#         elif condelem[2] == '>=':
#             return A >= B
#
#     condA = []
#     condB = []
#     oper = 'AND'
#     if condelem[0] == '(':
#         c = 0
#         p = 0
#         for cl in condelem:
#             if cl == '(':
#                 c = c + 1
#             elif cl == ')':
#                 c = c - 1
#             else:
#                 condA.append(cl)
#
#             if c == 0 and p < len(condelem) - 1:
#                 oper = condelem[p + 1]
#                 condB = condelem[p + 2 : ]
#                 break
#
#             p = p + 1
#     else:
#         condA = condelem[0:4]
#         oper = condelem[4]
#         condB = condelem[5:]
#
#
#
#     resA = evalcore(condA, idx)
#     if len(condB) != 0:
#         resB = evalcore(condB, idx)
#     else:
#         resB = True
#
#     if oper == 'AND':
#         return resA and resB
#     elif oper == 'OR':
#         return resA or resB
#
#     return False
#     pass

def evalcore(condelem, idx):

    if len(condelem) < 4:
        return False

    if len(condelem) == 4:
        vmap = getconvmap()
        type = condelem[0]
        try:
            A = vmap[condelem[1]][idx]
        except:
            return "excel_error" + condelem[1]
        B = condelem[3]

        if condelem[2] == 'is_diff_variable' or condelem[2] == 'is_equal_variable':
            try:
                B = vmap[condelem[3]][idx]
            except:
                return "excel_error" + condelem[3]

        if type == "number":
            try:
                A = int(A)
            except ValueError:
                A = 0
            try:
                B = int(B)
            except ValueError:
                B = 0

        if condelem[2] == '<':
            return A < B
        elif condelem[2] == '=':
            return A == B
        elif condelem[2] == '<=':
            return A <= B
        elif condelem[2] == '>':
            return A > B
        elif condelem[2] == '>=':
            return A >= B

        elif condelem[2] == 'contains':
            return B in A
        elif condelem[2] == 'not_contains':
            return B not in A
        elif condelem[2] == 'contains_num':
            return any(char.isdigit() for char in A)
        elif condelem[2] == 'not_contains_num':
            return not any(char.isdigit() for char in A)
        elif condelem[2] == 'start_capital':
            return A[0].isupper()
        elif condelem[2] == 'not_start_capital':
            return A[0].islower()
        elif condelem[2] == 'is_empty':
            return A == ''
        elif condelem[2] == 'is_not_empty':
            return A != ''
        elif condelem[2] == 'is_diff_variable':
            return A != B
        elif condelem[2] == 'is_equal_variable':
            return A == B

        elif condelem[2] == 'starts_with':
            return A.startswith(B)

    condA = []
    condB = []
    oper = ''
    if condelem[0] == '(':
        c = 0
        p = 0
        for cl in condelem:
            if cl == '(':
                c = c + 1
                if c != 1:
                    condA.append(cl)
            elif cl == ')':
                c = c - 1
                if c != 0:
                    condA.append(cl)
            else:
                condA.append(cl)

            if c == 0:
                if len(condelem) > p + 1:
                    oper = condelem[p + 1]
                    condB = condelem[p + 2 : ]
                break

            p = p + 1
    else:
        condA = condelem[0:4]
        if len(condelem) > 4:
            oper = condelem[4]
            condB = condelem[5:]


    resA = evalcore(condA, idx)
    resB = evalcore(condB, idx)
    if oper == 'AND':
        return resA and resB
    elif oper == 'OR':
        return resA or resB
    elif oper == '':
        if len(condA) > 0:
            return resA
        if len(condB) > 0:
            return resB

    return False



def evalcondition(condstr, idx):
    # first split the elements
    elements = []
    startword = False
    word = ''
    for i in range(len(condstr)):
        char = condstr[i]
        if char == '(' or char == ')':
            elements.append(char)
        elif char == '\'':
            if startword == False:
                startword = True
            else:
                if i == (len(condstr) - 1):
                    startword = False
                    elements.append(word)
                    word = ''
                elif condstr[i+1] == " " or condstr[i+1] == ")":
                    startword = False
                    elements.append(word)
                    word = ''
                else:
                    word = word + char
        elif char == ' ' and word != '' and startword == False:
            elements.append(word)
            word = ''
        else:
            if word != '' or char != ' ':
                word = word + char
    
    return evalcore(elements, idx)

def replaceonefile(sf, df, idx, novalrule, output_format, addptag, humanaction, editorial_method, showEmptySection):
    global notexistvariables
    global novaluefiles
    global novaluefiles
    global nopermutetags
    #global gvars
    vmap = getconvmap()

    gvars = getvariables()

    # get the destination file name
    idx = idx
    if df == "":
        dest_filename = str(idx + 1) + "-" + sf
    else:
        if len(vmap[df]) <= idx:
            dest_filename = sf
        else:
            dest_filename = vmap[df][idx].lower()

            dest_filename = dest_filename.replace('/', ' ')

            if dest_filename != "":
                if len(dest_filename) > 255:
                    dest_filename = str(idx + 1) + '''-''' + dest_filename[:255] + '''.txt'''
                else:
                    dest_filename = str(idx + 1) + "-" + dest_filename + ".txt"
            else:
                dest_filename = str(idx + 1) + "-" + sf

    sfp = open('uploads/origfiles/' + sf)
    # dfp = open('uploads/destfiles/' + df, "w")
    dfp = open('uploads/destfiles/' + dest_filename, "w")
    #dfp = open('uploads/destfiles/')
    origtext = sfp.read()
    inputtext = origtext
    result = EC.OK
    #seterrorstring(geterrorstring() + "+++++++++++ processing " + sf + " file start+++++++++++\n")

    # remove multi-space
    #origtext = ' '.join(origtext.split())

    # first replace variables to values.
    bvalid = True
    for (k, v) in vmap.items():
        if idx >= len(vmap[k]):
            bvalid = False
            break

        if k[0] == '$': # for valid variables, we can change.
            values = vmap[k][idx]
            values = "{}".format(values)

            comma_split_values = vmap[k][idx].split(',')
            comma_split_values_before_lastcomma = []
            for i in range(len(comma_split_values)):

                comma_split_values[i] = comma_split_values[i].strip()
                if i < len(comma_split_values) - 1:
                    comma_split_values_before_lastcomma.append(comma_split_values[i])
            shuffle_val = ', '.join(random.sample(comma_split_values,len(comma_split_values)))
            if len(comma_split_values) > 1:
                shuffle_and = ', '.join(random.sample(comma_split_values_before_lastcomma, len(comma_split_values_before_lastcomma))) + ' et ' + comma_split_values[len(comma_split_values) - 1]
                shuffle_or = ', '.join(random.sample(comma_split_values_before_lastcomma, len(comma_split_values_before_lastcomma))) + ' ou ' + comma_split_values[len(comma_split_values) - 1]
            else:
                shuffle_and = shuffle_val
                shuffle_or = shuffle_val

            if values != "":
                #shuffle change
                # origtext = origtext.replace('<shuffle>' + k + '</shuffle>', shuffle_val)
                # origtext = origtext.replace('<shuffle-and>' + k + '</shuffle-and>', shuffle_and)
                # origtext = origtext.replace('<shuffle-or>' + k + '</shuffle-or>', shuffle_or)

                #letter case functions
                # origtext = origtext.replace('<1st-letter-in-capital>' + k + '</1st-letter-in-capital>', vmap[k][idx].capitalize())
                # origtext = origtext.replace('<all-in-lower-case>' + k + '</all-in-lower-case>', vmap[k][idx].lower())
                # origtext = origtext.replace('<all-in-lower-case-except-1st>' + k + '</all-in-lower-case-except-1st>', vmap[k][idx].lower().capitalize())

                #origtext = origtext.replace('<sentence>' + k, vmap[k][idx].capitalize())

                #####    2020.09.02 modification for variable condition   #####
                #origtext = origtext.replace(k, vmap[k][idx])
                if k in varconditionList:
                    condition = varconditionList[k]

                    condition_content = condition['condition_content']
                    use_excel_for_fulfill = condition['use_excel_for_fulfill']
                    text_for_fulfill = condition['text_for_fulfill']
                    use_excel_for_not_fulfill = condition['use_excel_for_not_fulfill']
                    text_for_not_fulfill = condition['text_for_not_fulfill']

                    condres = evalcondition(condition_content, idx)

                    if (condres and use_excel_for_fulfill) or (condres == False and use_excel_for_not_fulfill):
                        origtext = origtext.replace(k, vmap[k][idx].strip())
                    else:
                        if condres and use_excel_for_fulfill == False:
                            rep_txt_list = text_for_fulfill.split('\n')
                        elif condres == False and use_excel_for_not_fulfill == False:
                            rep_txt_list = text_for_not_fulfill.split('\n')
                        num_vars = origtext.count(k)
                        for s in range(num_vars):
                            rand_str = rep_txt_list[random.randrange(len(rep_txt_list))]
                            origtext = origtext.replace(k, rand_str.strip(), 1)

                else:
                    origtext = origtext.replace(k, vmap[k][idx].strip())

            elif novalrule == True:
                origtext = origtext.replace(" " + k + ".", ".")
                origtext = origtext.replace(" " + k + " ", " ")
                origtext = origtext.replace(" " + k, "")
                origtext = origtext.replace(k + " ", "")
                origtext = origtext.replace(":" + k + ".", ".")
                origtext = origtext.replace(";" + k + ".", ".")
                origtext = origtext.replace("," + k + ".", ".")
                origtext = origtext.replace(k, "")

    if bvalid:
        # 2021 12.16 section reorder task   ===== start
        
        origtext = section_reorder(origtext)

        # 2021 12.16 section reorder task   ===== end
        
        # remove multi-space
        # origtext = ' '.join(origtext.split())

        # remove space and line between html close tag and new start tag
        #origtext = re.sub(">\s*<", "><", origtext)

        # apply <random-number-x-y>
        origtext = randomNumberXY(origtext)

        # make a </p> tag if it is not existed
        origtext = origtext.replace(" <p>", "</p><p>")

        # make a new line before <h1>, <h2>, <h3>, <h4>, <h5>, <h6>
        hstr = re.findall('[ |>][<]h[1-6][>]', origtext)
        if len(hstr) > 0:
            for title in hstr:
                newtitle = title[:1] + '\n\n' + title[-4:]
                origtext = origtext.replace(title, newtitle)

        # make a new line between html <p> tags
        hstr = re.findall('><P>', origtext)
        if len(hstr) > 0:
            for title in hstr:
                newtitle = title[:1] + '\n\n' + title[-3:]
                origtext = origtext.replace(title, newtitle)

        # New line for Meta description
        origtext = origtext.replace(' Meta description', '\n\nMeta description')

        origtext = origtext.replace(',.', '.')
        #origtext = origtext.replace('..', '.')
        #origtext = origtext.replace(' </', '</')
        origtext = origtext.replace('<p> ', '<p>')

        # replace variables with values
        notexistvar = re.findall('\$[a-z|0-9|A-Z|-]+', origtext)
        if len(notexistvar) > 0:
            #errstring = "There are variables in the {} files that we don't have in the Excel sheet.\n list of these variables are as follows:\n".format(sf)
            for i in range(len(notexistvar)):
                #errstring = errstring + notexistvarible[i] + "\n"
                if notexistvar[i] not in notexistvariables and notexistvar[i] not in gvars:
                    notexistvariables.append(notexistvar[i])

                    #seterrorstring(geterrorstring() + errstring)
                    result = EC.NoExistVariable

        # find conditions
        cond_items = re.findall('[<]cond-[^<]+[>]', origtext)

        cond_id_list = []
        for cond_item in cond_items:
            cond_id = cond_item[6:-1]
            cond_id_list.append(cond_id)
        cond_id_list = list(dict.fromkeys(cond_id_list))

        for cond_id in cond_id_list:
            if cond_id in conditionList:
                condition = conditionList[cond_id]
                
                condres = evalcondition(condition['cond'], idx)


                if isinstance(condres, str) and 'excel_error' in condres:

                    return condres
                newtext = ''
                cond_texts = re.findall(f'<cond-{cond_id}>[^*]*?<\/cond-{cond_id}>', origtext)
                for cond_text in cond_texts:
                    

                    if condres == True:

                        newtext = cond_text.replace(f'<cond-{cond_id}>', '').replace(f'</cond-{cond_id}>', '')

                    
                    if newtext == '':
                        origtext = origtext.replace('\n' + cond_text + '\n', newtext + '\n')
                        origtext = origtext.replace(cond_text, newtext)
                    else:
                        origtext = origtext.replace(cond_text, newtext)
            else:
                
                noconditions.append("<cond-" + cond_id + ">")

        # check permute tag pairs
        check_tags, permuteTagPaired = check_tags_pairs(inputtext, sf)
        if check_tags == False:

            nopermutetags.append(sf)
            if result == EC.NoExistVariable:
                result = EC.NoExistVariable_and_NoPairedtags
            else:
                result = EC.NoPairedtags        

        if permuteTagPaired == True:
            # permute function after injecting variables.
            
            origtext = perform_togetherPermute(origtext)
            origtext = perform_permute(origtext)
            origtext = clean_perform_permute(origtext)

        # 'Marseille 2e Arrondissement'  => 'dans le 2ème arrondissement de Marseille'
        origtext = cityNameChange(origtext)

        # 2022 10 19 <cluster-name>
        origtext = process_clusterTags(origtext, idx)


        # merge multi blank lines into 1
        origtext = re.sub(r'(\n\s*)+\n+', '\n\n', origtext)

        # remove blank lines in header and tail
        #origtext = origtext.rstrip("\n\n")
        origtext = origtext.strip("\n")        

        # apply replacement rules
        for order, rule in enumerate(cvrule):
            exceptions = rule["exceptions"].split(",")
            random_str = []
            for i in range(len(exceptions)):
                if len(exceptions) == 1 and exceptions[0] == "":
                    break
                random_str.append(randomString())
                insentive_src = re.compile(re.escape(exceptions[i]), re.IGNORECASE)
                origtext = insentive_src.sub(random_str[i], origtext)
            if rule["case_sen"] == True:
                #origtext = origtext.replace(rule['src'], rule['dest'])
                origtext = replacePattern(rule['src'], rule['dest'], origtext)
            else:
                insentive_src = re.compile(re.escape(rule['src']), re.IGNORECASE)
                origtext = insentive_src.sub(rule['dest'], origtext)

            for i in range(len(exceptions)):
                if len(exceptions) == 1 and exceptions[0] == "":
                    break
                origtext = origtext.replace(random_str[i], exceptions[i])

        # perform permute <li> tags
        origtext = perform_permute_liTags(origtext)

        # perform lower, uppper function
        origtext = perform_lower_uppper(origtext)

        # do this action if json output is false and humanaction is true
        if output_format != '2' and humanaction == True:

            dest_val = ''
            if df != '':
                if len(vmap[df]) <= idx:
                    dest_val = ''
                else:
                    dest_val = vmap[df][idx]
            origtext = delete_unuseful_sections(origtext, editorial_method, dest_val, showEmptySection)


        origtext = origtext.strip()

        # remove blank spaces at starting point in every lines
        # replace multi spaces with one space
        new_text = ''
        lines = origtext.split('\n')
        for line in lines:
            line = line.strip()
            line = re.sub('\s+', ' ', line)
            new_text += line + '\n'
        origtext = new_text

        # add p tag if the option is available
        if addptag == True and (output_format == '1' or output_format == '4'):

            if origtext.startswith('#start-'):
                
                origtext = origtext.replace('<h1>', '\n<h1>')
                origtext = origtext.replace('<h2>', '\n<h2>')
                origtext = origtext.replace('<h3>', '\n<h3>')
                origtext = origtext.replace('</h1>', '</h1>\n')
                origtext = origtext.replace('</h2>', '</h2>\n')
                origtext = origtext.replace('</h3>', '</h3>\n')

                lines = origtext.split('\n\n')
                if len(lines) > 1:
                    new_content = ''
                    for line in lines:
                        line = line.strip()
                        
                        if line.startswith('#start-') == True and line.startswith('#start-section') == True:
                            
                            if line.endswith('#') == True and len(line.split('\n')) > 1:
                                new_line = line.split('\n')[0] + '\n' + '<p>' + '\n'.join(line.split('\n')[1:-1]) + '</p>' + '\n' + line.split('\n')[-1] + '\n\n'
                            elif line.endswith('#') == False and len(line.split('\n')) > 1:                                    
                                new_line = line.split('\n')[0] + '\n' + '<p>' + '\n'.join(line.split('\n')[1:]) + '</p>'  + '\n\n'
                            elif len(line.split('\n')) == 1:
                                new_line = line + '\n'
                            
                        elif line.startswith('#start-') == True and line.startswith('#start-section') == False:
                            new_line = line + '\n\n'

                        elif line.startswith('#end-'):
                            new_line = line + '\n\n'

                        elif line.split('\n')[-1].startswith('#end-'):
                            new_line = '<p>' + '\n'.join(line.split('\n')[:-1])  + '</p>' + '\n' +  line.split('\n')[-1]  + '\n\n'

                        elif line.startswith('<no-p-tag>') and line.endswith('</no-p-tag>'):
                            new_line = line.replace('<no-p-tag>', '').replace('</no-p-tag>', '') + '\n\n'
                        elif line.startswith('<h'):
                            new_line = line + '\n\n'
                        else:
                            new_line = '<p>' + line + '</p>' + '\n\n'
                        new_content += new_line
                    origtext = new_content.strip()
                    # origtext = origtext.replace('\n<h1>', '<h1>')
                    # origtext = origtext.replace('\n<h2>', '<h2>')
                    # origtext = origtext.replace('\n<h3>', '<h3>')
                    origtext = origtext.replace('</h1>\n', '</h1>')
                    origtext = origtext.replace('</h2>\n', '</h2>')
                    origtext = origtext.replace('</h3>\n', '</h3>')

            else:

                lines = origtext.split('\n\n')
                if len(lines) > 1:
                    new_content = ''
                    for line in lines:
                        line = line.strip()
                        if line.startswith('META TITLE :') or line.startswith('META DESCRIPTION :') or line.startswith('<h') or line.startswith('<p>') or line.startswith('TITRE'):
                            new_line = line + '\n\n'
                        
                        elif line.startswith('<no-p-tag>') and line.endswith('</no-p-tag>'):
                            new_line = line.replace('<no-p-tag>', '').replace('</no-p-tag>', '') + '\n\n'

                        else:
                            new_line = '<p>' + line + '</p>' + '\n\n'
                        new_content += new_line
                    origtext = new_content.strip()

        # if putput is to strip json tags
        elif output_format == '3':
            origtext = strip_jsontags(origtext, addptag)

        # merge multi blank lines into 1
        origtext = re.sub(r'(\n\s*)+\n+', '\n\n', origtext)

        # remove blank lines in header and tail
        origtext = origtext.strip("\n")

    else:
        novaluefiles.append(sf)

    #seterrorstring(geterrorstring() + "+++++++++++ processing " + sf + " file end+++++++++++\n\n")
    dfp.write(origtext)
    sfp.close()
    dfp.close()
    return result

def process_clusterTags(origtext, idx):
    global clusterconditionList

    
    items = re.findall('<cluster-[^*]*?</cluster-', origtext)
    
    for item in items:
        clusterId = item.split(">")[0].replace("<cluster-", "")
        oldStr = item + clusterId + ">"

        if clusterId in clusterconditionList.keys():    
            condition = clusterconditionList[clusterId]

            condition_content = condition['condition_content']            
            text_for_fulfill = condition['text_for_fulfill']            
            text_for_not_fulfill = condition['text_for_not_fulfill']

            condres = evalcondition(condition_content, idx)
           
            if condres == True:
                rep_txt_list = text_for_fulfill.split('\n')
            else:
                rep_txt_list = text_for_not_fulfill.split('\n')
            num_vars = origtext.count(oldStr)
            for s in range(num_vars):
                rand_str = rep_txt_list[random.randrange(len(rep_txt_list))]
                origtext = origtext.replace(oldStr, rand_str.strip(), 1)

    return origtext

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

def perform_permute_liTags(text):
    per_texts = re.findall('<permute-list>[^*]*?</permute-list>', text)

    for per_text in per_texts:
        
        per_str = per_text.replace("<permute-list>", "").replace("</permute-list>", "")

        ul_list = re.findall('<ul>[^*]*?</ul>', per_str)
        if (len(ul_list) == 1):
            ul_str = ul_list[0]
            li_list = re.findall('<li>[^*]*?</li>', ul_str)

            permute_li_list = random.sample(li_list, len(li_list))
            new_permute_li = ""
            for index, permute_li in enumerate( permute_li_list ):
                li_str = permute_li.replace('<li>', '').replace('</li>', '').strip()
                if li_str.split(".")[0].isdigit():
                    new_li_str = li_str.replace(li_str.split(".")[0] + ".", str(index+1) + ".")
                    new_li = "<li>" + new_li_str + "</li>"

                    new_permute_li += new_li

            text = text.replace(per_text, "<ul>" + new_permute_li + "</ul>")

    return text

def section_reorder(origtext):

    items = re.findall('#start-[^*]*?#end-', origtext)

    section_index = 0
    for item in items:
        
        para_id = item.split('#')[1].replace('start-', '')
        para_content = item.split('#start-' + para_id + '#')[1].replace('#end-', '')

        if para_id.startswith('section'):
            section_index += 1

            new_para_id = 'section' + str(section_index)

            old_section = item + para_id + '#'
            new_section = '#start-' + new_para_id + '#' + para_content + '#end-' + new_para_id + '#'

            origtext = origtext.replace(old_section, new_section)

    return origtext


def cityNameChange(origtext):
    CITY_LIST = ['Marseille', 'Lyon', 'Paris']
    for city_name in CITY_LIST:
        per_texts = re.findall(f'{city_name} [0-9]+e Arrondissement', origtext)
        for per_text in per_texts:
            number = per_text.split()[1].replace('e', '')
            newtext = f'dans le {number}ème arrondissement de ' + city_name
            origtext = origtext.replace(per_text, newtext)
    return origtext

def randomNumberXY(origtext):
    items = re.findall('<random-number-\d+-\d+>', origtext)
    for item in items:
        num1 = int(item.split('-')[2])
        num2 = int(item.split('-')[3].replace('>', ''))
        if num1 > num2:
            continue
        randon_num = str(random.randint(num1,num2))
        origtext = origtext.replace(item, randon_num, 1)
    return origtext

def delete_unuseful_sections(origtext, editorial_method, dest_val, showEmptySection):
    if dest_val != '':
        dest_val = ' - ' + dest_val
    items = re.findall('#start-[^*]*?#end-', origtext)
    
    if len(items) == 0:
        return origtext
    for index, item in enumerate( items ):
        para_id = item.split('#')[1].replace('start-', '')
        para_content = item.split('#start-' + para_id + '#')[1].replace('#end-', '')

        # merge multi blank lines into 1
        new_para_content = re.sub(r'(\n\s*)+\n+', '\n', para_content)
        new_para_content = new_para_content.strip()

        print("showEmptySection", showEmptySection)
        if showEmptySection == False and new_para_content == "":
            header_line = ''            
        else:
            header_line = f'{para_id.upper()}{dest_val}'

        if editorial_method == '0':
            if index > 0:
                dest_val = ''
            if 'section' in para_id or 'introduction' in para_id or 'conclusion' in para_id:
                origtext = origtext.replace(f'#start-{para_id}#{para_content}#end-{para_id}#', f'{header_line}\n{new_para_content.strip()}')
            elif 'texte' in para_id:
                origtext = origtext.replace(f'#start-{para_id}#{para_content}#end-{para_id}#', f'{header_line}\n{new_para_content.strip()}')
            elif 'titre' in para_id:
                origtext = origtext.replace(f'#start-{para_id}#{para_content}#end-{para_id}#', f'{header_line}\n{new_para_content.strip()}')
            elif para_id == 'meta_title' or para_id == 'meta-title':
                origtext = origtext.replace(f'#start-{para_id}#{para_content}#end-{para_id}#', f'META TITLE{dest_val}\n{new_para_content.strip()}')
            elif para_id == 'meta_description' or para_id == 'meta-description':
                origtext = origtext.replace(f'#start-{para_id}#{para_content}#end-{para_id}#', f'META DESCRIPTION{dest_val}\n{new_para_content.strip()}')
            elif para_id in ['h1', 'h2', 'h3', 'h4', 'h5']:
                
                origtext = origtext.replace(f'#start-{para_id}#{para_content}#end-{para_id}#', f'{para_id.upper()}{dest_val}\n{new_para_content.strip()}')
            else:
                origtext = origtext.replace(f'#start-{para_id}#{para_content}#end-{para_id}#', '')

        else:
            if 'section' in para_id or 'introduction' in para_id or 'conclusion' in para_id:
                # new_para_content = para_content.replace("\n", "\n\n")
                origtext = origtext.replace(f'#start-{para_id}#{para_content}#end-{para_id}#', new_para_content.strip())
            elif 'texte' in para_id:
                origtext = origtext.replace(f'#start-{para_id}#{para_content}#end-{para_id}#', new_para_content.strip())
            elif 'titre' in para_id:
                origtext = origtext.replace(f'#start-{para_id}#{para_content}#end-{para_id}#', new_para_content.strip())
            # elif para_id == 'meta_title' or para_id == 'meta-title':
            #     origtext = origtext.replace(f'#start-{para_id}#{para_content}#end-{para_id}#', para_content.strip())
            # elif para_id == 'meta_description' or para_id == 'meta-description':
            #     origtext = origtext.replace(f'#start-{para_id}#{para_content}#end-{para_id}#', para_content.strip())
            elif para_id == 'meta_title' or para_id == 'meta-title':
                origtext = origtext.replace(f'#start-{para_id}#{para_content}#end-{para_id}#', f'META TITLE{dest_val}\n{new_para_content.strip()}')
            elif para_id == 'meta_description' or para_id == 'meta-description':
                origtext = origtext.replace(f'#start-{para_id}#{para_content}#end-{para_id}#', f'META DESCRIPTION\n{new_para_content.strip()}')
            
            elif para_id in ['h1', 'h2', 'h3', 'h4', 'h5']:                
                origtext = origtext.replace(f'#start-{para_id}#{para_content}#end-{para_id}#', "TITRE H1" + "\n" + new_para_content.strip().upper())
            else:
                origtext = origtext.replace(f'#start-{para_id}#{para_content}#end-{para_id}#', '')

    #make upper case for h1. h2, h3, h4, h5 titles.
    # if editorial_method == '0':
    h_items = re.findall('<h[1-6][>][^*]*?</h', origtext)
    for item in h_items:
        h_n = item.split('>')[0].replace('<h', '')
        h_content = item.split('>')[1].replace('</h', '')
        origtext = origtext.replace(f'<h{h_n}>{h_content}</h{h_n}>', '\n' + h_content.upper().strip() + '\n')
        origtext = origtext.replace(h_content.upper().strip() + '\n\n', h_content.upper().strip() + '\n')

    # <title>blabla</title> => BLABLA
    items = re.findall('<title>[^*]*?</title>', origtext)
    for item in items:
        title = item.replace('<title>', '').replace('</title>', '')
        origtext = origtext.replace(item, '\n' + title.upper().strip())
    
    name_items = re.findall('<name>[^*]*?</name>', origtext)
    for name_item in name_items:
        origtext = origtext.replace(name_item, "")

    tag_items = re.findall('<[^*]*?>', origtext)
    for tag_item in tag_items:
        origtext = origtext.replace(tag_item, "")

    return origtext

def check_tags_pairs(text, sf):
    global nopairedtags
    tags = re.findall('<[^*]*?>', text)
    start_tags = []
    for tag in tags:
        tag = tag.replace('</', '<')
        if tag not in start_tags:
            start_tags.append(tag)

    val = True
    for start_tag in start_tags:
        if start_tag.startswith('<a href') or start_tag.startswith('<img src'):
            continue
        if start_tag.startswith('<a>') or start_tag.startswith('<img>'):
            continue
        end_tag = start_tag.replace('<', '</')
        start_list = re.findall(start_tag, text)
        end_list = re.findall(end_tag, text)
        if len(start_list) != len(end_list):
            val = False
            # if start_tag not in nopairedtags:
            #     nopairedtags.append(start_tag + ": " + sf)
            # if end_tag not in nopairedtags:
            #     nopairedtags.append(end_tag + ": " + sf)

            if len(start_list) > len(end_list):
                unmatched_strs = re.findall(start_tag + '[^*]*?' + start_tag, text)
                for unmatched_str in unmatched_strs:
                    if unmatched_str not in nopairedtags and end_tag not in unmatched_str:
                        lineOftag = len(text.split(unmatched_str)[0].split('\n'))
                        nopairedtags.append(f"{start_tag}: line {lineOftag} of {sf}" )
            elif len(start_list) < len(end_list):
                unmatched_strs = re.findall(end_tag + '[^*]*?' + end_tag, text)
                for unmatched_str in unmatched_strs:
                    if unmatched_str not in nopairedtags and start_tag not in unmatched_str:
                        lineOftag = len(text.split(unmatched_str)[0].split('\n'))
                        nopairedtags.append(f"{end_tag}: line {lineOftag} of {sf}" )


    permuteTagPaired = True
    for nopairedtag in nopairedtags:
        if 'permute' in nopairedtag:
            permuteTagPaired = False
            break
    return val, permuteTagPaired

def perform_togetherPermute(text):
    
    per_texts = re.findall('<together>[^*]*?</together>', text)    
    for per_text in per_texts:
        
        per_str_origin = per_text.replace("<together>", "")
        per_str_origin = per_str_origin.replace("</together>", "")

        per_str_origin = perform_permute(per_str_origin)
        per_str_origin = per_str_origin.replace(",", "together-comma")
        per_str_origin = per_str_origin.replace(" et ", "together-et")
        per_str_origin = per_str_origin.replace(" ou ", "together-ou")

        text = text.replace(per_text, per_str_origin)

    return text

def clean_perform_permute(text):
    text = text.replace("together-comma", ",")
    text = text.replace("together-et", " et ")
    text = text.replace("together-ou", "together-ou")
    return text

def perform_permute(text):
    #per_texts = re.findall('[<]permute[^<]+[<]', text)
    per_texts = re.findall('<permute[^*]*?</permute', text)
    # per_texts = re.findall('<permute>[^<]+[<]', text)
    for per_text in per_texts:
        #print(per_text)
        #param = per_text.split('>')[0].split('<')[1].strip()
        # print(param)
        #per_str = per_text.split('>')[1].split('<')[0].strip()
        per_str_origin = per_text.split('>')[1].split('</permute')[0]
        per_id = per_text.split('>')[0].replace('<permute', '')

        # replace 'et' and 'ou' with comma
        per_str = per_str_origin.replace(' et ', ',').replace(' ou ', ',')

        comma_split_values = per_str.split(',')
        comma_split_values = random.sample(comma_split_values, len(comma_split_values))
        comma_split_values_before_lastcomma = []
        for i in range(len(comma_split_values)):

            comma_split_values[i] = comma_split_values[i].strip()
            if i < len(comma_split_values) - 1:
                comma_split_values_before_lastcomma.append(comma_split_values[i])
        permute_val = ', '.join(random.sample(comma_split_values, len(comma_split_values)))
        if len(comma_split_values) > 1:
            permute_and = ', '.join(
                random.sample(comma_split_values_before_lastcomma, len(comma_split_values_before_lastcomma))) + ' et ' + \
                          comma_split_values[len(comma_split_values) - 1]
            permute_or = ', '.join(
                random.sample(comma_split_values_before_lastcomma, len(comma_split_values_before_lastcomma))) + ' ou ' + \
                         comma_split_values[len(comma_split_values) - 1]
        else:
            permute_and = per_str_origin
            permute_or = per_str_origin

        permute_3_5 = permute_3_4 = permute_2_4 = permute_3_3 = permute_2_3 = permute_val
        permute_3_5_and = permute_3_4_and = permute_2_4_and = permute_3_3_and = permute_2_3_and = permute_and
        permute_3_5_or = permute_3_4_or = permute_2_4_or = permute_3_3_or = permute_2_3_or = permute_or

        if len(comma_split_values) > 4:
            permute_3_5 = ', '.join(random.sample(comma_split_values, randint(3, 5)))
            permute_3_5_and = ', '.join(random.sample(comma_split_values_before_lastcomma, randint(2, 4))) + ' et ' + comma_split_values[
                len(comma_split_values) - 1]
            permute_3_5_or = ', '.join(random.sample(comma_split_values_before_lastcomma, randint(2, 4))) + ' ou ' + comma_split_values[
                len(comma_split_values) - 1]

        if len(comma_split_values) > 3:
            permute_3_4 = ', '.join(random.sample(comma_split_values, randint(3, 4)))
            permute_3_4_and = ', '.join(random.sample(comma_split_values_before_lastcomma, randint(2, 3))) + ' et ' + comma_split_values[
                len(comma_split_values) - 1]
            permute_3_4_or = ', '.join(random.sample(comma_split_values_before_lastcomma, randint(2, 3))) + ' ou ' + comma_split_values[
                len(comma_split_values) - 1]

            permute_2_4 = ', '.join(random.sample(comma_split_values, randint(2, 4)))
            permute_2_4_and = ', '.join(random.sample(comma_split_values_before_lastcomma, randint(1, 3))) + ' et ' + comma_split_values[
                len(comma_split_values) - 1]
            permute_2_4_or = ', '.join(random.sample(comma_split_values_before_lastcomma, randint(1, 3))) + ' ou ' + comma_split_values[
                len(comma_split_values) - 1]

        elif len(comma_split_values) == 3:
            permute_2_4 = ', '.join(random.sample(comma_split_values, randint(2, 3)))
            permute_2_4_and = ', '.join(random.sample(comma_split_values_before_lastcomma, randint(1, 2))) + ' et ' + comma_split_values[
                len(comma_split_values) - 1]
            permute_2_4_or = ', '.join(random.sample(comma_split_values_before_lastcomma, randint(1, 2))) + ' ou ' + comma_split_values[
                len(comma_split_values) - 1]            

        if len(comma_split_values) > 2:
            permute_3_3 = ', '.join(random.sample(comma_split_values, 3))
            permute_3_3_and = ', '.join(random.sample(comma_split_values_before_lastcomma, 2)) + ' et ' + comma_split_values[
                len(comma_split_values) - 1]
            permute_3_3_or = ', '.join(random.sample(comma_split_values_before_lastcomma, 2)) + ' ou ' + comma_split_values[
                len(comma_split_values) - 1]

            permute_2_3 = ', '.join(random.sample(comma_split_values, randint(2, 3)))
            permute_2_3_and = ', '.join(random.sample(comma_split_values_before_lastcomma, randint(1, 2))) + ' et ' + comma_split_values[
                len(comma_split_values) - 1]
            permute_2_3_or = ', '.join(random.sample(comma_split_values_before_lastcomma, randint(1, 2))) + ' ou ' + comma_split_values[
                len(comma_split_values) - 1]

        text = text.replace(f'<permute>{per_str_origin}</permute>', permute_val)
        text = text.replace(f'<permute-and>{per_str_origin}</permute-and>', permute_and)
        text = text.replace(f'<permute-or>{per_str_origin}</permute-or>', permute_or)

        text = text.replace(f'<permute-3-5>{per_str_origin}</permute-3-5>', permute_3_5)
        text = text.replace(f'<permute-3-5-and>{per_str_origin}</permute-3-5-and>', permute_3_5_and)
        text = text.replace(f'<permute-3-5-or>{per_str_origin}</permute-3-5-or>', permute_3_5_or)

        text = text.replace(f'<permute-3-4>{per_str_origin}</permute-3-4>', permute_3_4)
        text = text.replace(f'<permute-3-4-and>{per_str_origin}</permute-3-4-and>', permute_3_4_and)
        text = text.replace(f'<permute-3-4-or>{per_str_origin}</permute-3-4-or>', permute_3_4_or)

        text = text.replace(f'<permute-3-3>{per_str_origin}</permute-3-3>', permute_3_3)
        text = text.replace(f'<permute-3-3-and>{per_str_origin}</permute-3-3-and>', permute_3_3_and)
        text = text.replace(f'<permute-3-3-or>{per_str_origin}</permute-3-3-or>', permute_3_3_or)

        text = text.replace(f'<permute-2-3>{per_str_origin}</permute-2-3>', permute_2_3)
        text = text.replace(f'<permute-2-3-and>{per_str_origin}</permute-2-3-and>', permute_2_3_and)
        text = text.replace(f'<permute-2-3-or>{per_str_origin}</permute-2-3-or>', permute_2_3_or)

        text = text.replace(f'<permute-2-4>{per_str_origin}</permute-2-4>', permute_2_4)
        text = text.replace(f'<permute-2-4-and>{per_str_origin}</permute-2-4-and>', permute_2_4_and)
        text = text.replace(f'<permute-2-4-or>{per_str_origin}</permute-2-4-or>', permute_2_4_or)
    return text
    
def perform_lower_uppper(text):
    re_texts = re.findall('<1st-letter-in-capital>[^*]*?</1st-letter-in-capital>', text)
    for re_text in re_texts:
        #param = re_text.split('>')[0].split('<')[1].strip()
        # print(param)
        re_str = re_text.split('<1st-letter-in-capital>')[1].split('</1st-letter-in-capital>')[0]
        text = text.replace(f'<1st-letter-in-capital>{re_str}</1st-letter-in-capital>', re_str.capitalize())

    re_texts = re.findall('<first-letter-in-capital>[^*]*?</first-letter-in-capital>', text)
    for re_text in re_texts:
        
        re_str = re_text.split('<first-letter-in-capital>')[1].split('</first-letter-in-capital>')[0]
        text = text.replace(f'<first-letter-in-capital>{re_str}</first-letter-in-capital>', re_str.capitalize())

    re_texts = re.findall('<all-in-lower-case>[^*]*?</all-in-lower-case>', text)
    for re_text in re_texts:
        #param = re_text.split('>')[0].split('<')[1].strip()
        # print(param)
        re_str = re_text.split('<all-in-lower-case>')[1].split('</all-in-lower-case>')[0]
        text = text.replace(f'<all-in-lower-case>{re_str}</all-in-lower-case>', re_str.lower())

    re_texts = re.findall('<all-in-lower-case-except-1st>[^*]*?</all-in-lower-case-except-1st>', text)
    for re_text in re_texts:
        #param = re_text.split('>')[0].split('<')[1].strip()
        # print(param)
        re_str = re_text.split('<all-in-lower-case-except-1st>')[1].split('</all-in-lower-case-except-1st>')[0]
        text = text.replace(f'<all-in-lower-case-except-1st>{re_str}</all-in-lower-case-except-1st>',
                            re_str.lower().capitalize())
    return text

def configCVRule(project_name):
    global cvrule
    datas = CR.objects.raw(""
                           "SELECT "
                           "    no,"   
                           "    srcpattern, "
                           "    destpattern, "
                           "    case_sensitive, "
                           "    exceptions, "
                           "    priority "
                           "FROM "
                           "    managetemplate_conversionrule "
                           "WHERE "
                           "    enabled = 1 "
                           "AND "
                           "    project_name = '{}' "
                           "ORDER BY "
                           "    priority;".format(project_name))
    datas = list(datas)
    cvrule = []
    for data in datas:
        cvrule.append({
            "src": data.srcpattern,
            "dest": data.destpattern,
            "case_sen": data.case_sensitive,
            "exceptions": data.exceptions
        })


def loadConditionList(project_name):
    global conditionList
    #datas = CL.objects.all()
    datas = CL.objects.raw(""
                           "SELECT "
                           "    * "                           
                           "FROM "
                           "    managetemplate_condition "
                           "WHERE "
                           "    project_name = '{}' ".format(project_name))
    datas = list(datas)
    conditionList = {}
    for data in datas:
        conditionList[data.condition_id] = {
            "cond": data.condition_content,
            "res": False,
            "eval": False
        }

def loadVarConditionList(project_name):
    global varconditionList
    #datas = CL.objects.all()
    datas = VARCD.objects.raw(""
                           "SELECT "
                           "    * "                           
                           "FROM "
                           "    managetemplate_variablecondition "
                           "WHERE "
                           "    project_name = '{}' ".format(project_name))
    datas = list(datas)
    varconditionList = {}
    for data in datas:
        varconditionList[data.variable_name] = {
            "use_excel_for_fulfill": data.use_excel_for_fulfill,
            "text_for_fulfill": data.text_for_fulfill,
            "use_excel_for_not_fulfill": data.use_excel_for_not_fulfill,
            "text_for_not_fulfill": data.text_for_not_fulfill,
            "condition_content": data.condition_content,
            "res": False,
            "eval": False
        }

def loadClusterConditionList(project_name):
    global clusterconditionList
    #datas = CL.objects.all()
    datas = ClusterCondition.objects.raw(""
                           "SELECT "
                           "    * "                           
                           "FROM "
                           "    cluster_clustercondition "
                           "WHERE "
                           "    project_name = '{}' ".format(project_name))
    datas = list(datas)
    clusterconditionList = {}
    for data in datas:
        clusterconditionList[data.variable_name] = {            
            "text_for_fulfill": data.text_for_fulfill,            
            "text_for_not_fulfill": data.text_for_not_fulfill,
            "condition_content": data.condition_content,
            "res": False,
            "eval": False
        }

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
                    elif para.startswith('<no-p-tag>'):
                        new_para = para.replace('<no-p-tag>', '').replace('</no-p-tag>', '') + '\n\n'
                    else:
                        new_para = '<p>' + para + '</p>' + '\n\n'
                    new_para_content += new_para
                para_content = new_para_content.strip()
        origtext = origtext.replace(old_str, para_content)
    return origtext


def move_element(odict, thekey):
    ndict = {}

    for key, value in odict.items():
        if key == thekey:
            ndict[key] = odict[key]
            break
    for key, value in odict.items():
        if key != thekey:
            ndict[key] = odict[key]

    return ndict

def createJson(src_path, dest_path, result_file_name, addptag):
    data = []
    for file_title in os.listdir(src_path):
        if file_title.endswith('.txt'):
            file_path = os.path.join(src_path, file_title)
            sfp = open(file_path)
            origtext = sfp.read()
            items = re.findall('#start-[^*]*?#end-', origtext)
            dic = {}
            for item in items:
                para_id = item.split('#')[1].replace('start-', '')
                para_content = item.split('#start-' + para_id + '#')[1].replace('#end-', '').strip()

                first_row = para_content.split('\n')[0]
                if first_row.isupper():
                    para_content = para_content.replace(first_row, '').strip()

                if addptag == True:
                    paras = para_content.split('\n\n')
                    if len(paras) > 1 or 'section' in para_id or 'text' in para_id or 'paragraph' in para_id or 'intro' in para_id or 'conclusion' in para_id:

                        new_para_content = ''
                        for para in paras:
                            para = para.strip()
                            if para == '':
                                continue
                            if para.startswith('<h'):
                                new_para = para
                            elif para.startswith('<no-p-tag>'):
                                new_para = para.replace('<no-p-tag>', '').replace('</no-p-tag>', '') + '\n\n'
                            elif 'title' in para_id:
                                new_para = para
                            else:
                                new_para = '<p>' + para + '</p>'
                            new_para_content += new_para
                        para_content = new_para_content.strip()

                # # 2021 12-16 section-reorder added
                # section_title = re.findall('<title>[^*]*?</title>', para_content)
                # if len(section_title) > 0:
                #     title_para_id = para_id + '-title'
                #     title_para_content = section_title[0].replace('<title>', '').replace('</title>', '').strip()
                #     dic[title_para_id] = title_para_content

                #     dic[para_id] = para_content.replace(section_title[0], '').strip()
                # # 2021 12-16 section-reorder end.

                # else:
                dic[para_id] = para_content

            if 'url' in dic.keys():
                dic = move_element(dic, 'url')
            if 'uid' in dic.keys():
                dic = move_element(dic, 'uid')
            data.append(dic)
    file_path = os.path.join(dest_path, result_file_name)
    with open(file_path, 'w') as f:
        json.dump(data, f, ensure_ascii=False)
        f.close()

def createTxt(src_path, dest_path, result_file_name, addptag):
    data = []

    dash = '\n\n----------\n'
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

def countwords(origtext):
    return len(origtext.split())

def get_filename_words_list(filedir, ordertype):
    origfiles = [f for f in listdir(filedir) if isfile(join(filedir, f))]
    arr = []
    for i in range(len(origfiles)):
        sf = origfiles[i]
        sfp = open(join(filedir, sf))
        origtext = sfp.read()
        count_words = countwords(origtext)
        arr.append([sf, count_words])
    if ordertype == '0':
        arr = sorted(arr, key=lambda x: x[1], reverse=False)
    else:
        arr = sorted(arr, key=lambda x: x[1], reverse=True)
    filename_words_list = {}
    for i, item in enumerate(arr):
        filename_words_list[item[0]] = i + 1
    return filename_words_list

def replacevariables(zipfile, destfilename, novalrule, output_format, addptag, project_name, ordername, ordertype, humanaction, editorial_method, showEmptySection):
    global notexistvariables
    global novaluefiles
    global noconditions
    global nopermutetags
    global nopairedtags

    # if unzip(zipfile, 'uploads/origfiles') == False:
    #     return EC.UnZipFail

    if ordername != '':
        filename_words_list = get_filename_words_list('uploads/origfiles', ordertype)


    result = EC.OK
    notexistvariables = []
    novaluefiles = []
    noconditions = []
    nopermutetags = []
    nopairedtags = []

    origfiles = [f for f in listdir('uploads/origfiles') if isfile(join('uploads/origfiles', f))]
    configCVRule(project_name)
    loadConditionList(project_name)
    loadVarConditionList(project_name)
    loadClusterConditionList(project_name)
    # first replace all files
    global check_process
    for i in range(len(origfiles)):
        sf = origfiles[i]
        if ordername == '':
            # filenumber = re.findall('\d+', sf)
            # filenumber = filenumber[len(filenumber) - 1]
            filenumber = i + 1
        else:
            filenumber = filename_words_list[sf]
        if len(sf) < 5 or sf[-4:] != ".txt":
            return EC.InvalidTxt

        df = destfilename

        # if destfilename != "":
        #     df = destfilename + filenumber + ".txt"

        res = replaceonefile(sf, df, int(filenumber) - 1, novalrule, output_format, addptag, humanaction, editorial_method, showEmptySection)
        if isinstance(res, str) and 'excel_error' in res:
            return res
        if res != EC.OK:
            result = res

        check_process = i + 1

    if len(notexistvariables) > 0:
        errormsg = "There are variables in some txt files that we don't have in the Excel sheet:\n"
        for i in range(len(notexistvariables)):
            errormsg = errormsg + notexistvariables[i] + "\n"
        errormsg = errormsg + "\n"
        seterrorstring(geterrorstring() + errormsg)

    if len(novaluefiles) > 0:
        errormsg = "There are {} text files that we don't have values in the Excel sheet:\n".format(len(novaluefiles))
        for i in range(len(novaluefiles)):
            errormsg = errormsg + novaluefiles[i] + "\n"
            if i >= 2:
                errormsg = errormsg + "...\n"
                break
        errormsg = errormsg + "\n"
        seterrorstring(geterrorstring() + errormsg)

    noconditions = list(dict.fromkeys(noconditions))
    if len(noconditions) > 0:
        errormsg = "There are {} conditions that we don't have in the conditions list:\n".format(len(noconditions))
        for i in range(len(noconditions)):
            errormsg = errormsg + noconditions[i] + "\n"

        errormsg = errormsg + "\n"

        seterrorstring(geterrorstring() + errormsg)

    if len(nopairedtags) > 0:
        errormsg = "There are {} tags that are not paired:\n".format(len(nopairedtags))
        for i in range(len(nopairedtags)):
            errormsg = errormsg + nopairedtags[i] + "\n"

        errormsg = errormsg + "\n"

        seterrorstring(geterrorstring() + errormsg)

    # last zip result files.
    tz_paris = pytz.timezone('Europe/Paris')
    now = datetime.now(tz_paris)

    # if output format is a zip with all texts
    if output_format == '1' or output_format == '3':
        result_file_name = "resultat-final-" + '{:02d}'.format(now.day) + "-" + '{:02d}'.format(now.month) + "-" + str(now.year) + "-" + '{:02d}'.format(now.hour) + "h" + '{:02d}'.format(now.minute) + ".zip"
        #file_root = "static/" + result_file_name
        file_root = "static/result/" + result_file_name
        zip('uploads/destfiles', file_root)

    # if output format is json output
    elif output_format == '2':
        result_file_name = "resultat-final-" + '{:02d}'.format(now.day) + "-" + '{:02d}'.format(now.month) + "-" + str(
            now.year) + "-" + '{:02d}'.format(now.hour) + "h" + '{:02d}'.format(now.minute) + ".json"
        createJson('uploads/destfiles', 'static/result', result_file_name, addptag)
        file_root = "static/result/" + result_file_name

    # if output format is to gather all texts in 1 txt
    elif output_format == '4':
        result_file_name = "resultat-final-" + '{:02d}'.format(now.day) + "-" + '{:02d}'.format(now.month) + "-" + str(
            now.year) + "-" + '{:02d}'.format(now.hour) + "h" + '{:02d}'.format(now.minute) + ".txt"
        createTxt('uploads/destfiles', 'static/result', result_file_name, addptag)
        file_root = "static/result/" + result_file_name


    set_download_root(file_root)
    return result

def get_valuenow():
    global check_process   
    return check_process

def cleanAllText():
    result = EC.OK

    origfiles = [f for f in listdir('uploads/origfiles') if isfile(join('uploads/origfiles', f))]
    
    for i in range(len(origfiles)):
        sf = origfiles[i]        
        if len(sf) < 5 or sf[-4:] != ".txt":
            return EC.InvalidTxt

        df = sf

        # if destfilename != "":
        #     df = destfilename + filenumber + ".txt"

        res = cleanOneText(sf, df)

    # last zip result files.
    tz_paris = pytz.timezone('Europe/Paris')
    now = datetime.now(tz_paris)
   
    result_file_name = "extraction des textes " + '{:02d}'.format(now.day) + "-" + '{:02d}'.format(now.month) + "-" + str(now.year) + "-" + '{:02d}'.format(now.hour) + "h" + '{:02d}'.format(now.minute) + ".zip"
    #file_root = "static/" + result_file_name
    file_root = "static/result/" + result_file_name
    zip('uploads/destfiles', file_root)

    set_download_root(file_root)
    return result

def cleanOneText(sf, df):
    

    sfp = open('uploads/origfiles/' + sf)    
    dfp = open('uploads/destfiles/' + df, "w")
    
    origtext = sfp.read()
    items = re.findall('#start-[^*]*?#end-', origtext)

    for item in items:
        para_id = item.split('#')[1].replace('start-', '')
        para_content = item.split('#start-' + para_id + '#')[1].replace('#end-', '')
        section_content = item + para_id + '#'
        
        if 'image' in para_id:                
            origtext = origtext.replace(section_content, '')

        elif para_id == 'url':
            origtext = origtext.replace(section_content, '')

        elif para_id == 'meta_description':
            origtext = origtext.replace(section_content, '')

        else:
            origtext = origtext.replace(section_content, para_content)

    # remove all tags
    tags = re.findall('<[^*]*?>', origtext)
    for tag in tags:
        origtext = origtext.replace(tag, "")

    # merge multi blank lines into 1
    origtext = re.sub(r'(\n\s*)+\n+', '\n\n', origtext)

    # remove blank lines in header and tail
    origtext = origtext.strip("\n")
    
    result = EC.OK
    
    dfp.write(origtext)
    sfp.close()
    dfp.close()
    return result
