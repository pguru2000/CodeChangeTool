from xlrd import open_workbook, XLRDError
import xlwt
import re
import unicodedata
import pytz
from datetime import datetime

from utils.errorcode import ErrorCode as EC
from utils.errorcode import geterrorstring
from utils.errorcode import seterrorstring

from utils.download_root import set_download_root

import pandas as pd
import numpy as np 


UPLOAD_PATH = 'uploads/slug_generator/'
StaticFile_PATH = 'uploads/static/'
convmap = {}
varheader = []


def getconvmap():
    return convmap


def getvariables():
    return varheader


def readxlsfile(path):
    pass


def isexcelfile(filename):
    try:
        open_workbook(filename)
    except XLRDError:
        return False
    else:
        return True
    pass


def initmap():
    global convmap
    global varheader
    convmap = {}
    varheader = []


def configmap(filename):
    global varheader
    global convmap
    if isexcelfile(filename) == False:
        return EC.InvalidExcel

    try:
        workbook = open_workbook(filename)
        worksheet = workbook.sheet_by_index(0)
        initmap()
        convmap = {}
        varheader = []
        #bContinue = True
        c = 0
        # first read all variables
        cols = worksheet.ncols
        for c in range(cols):
            cell = worksheet.cell(0, c).value.strip()
            if cell == '':
                break
            if cell in varheader:
                si = varheader.index(cell)
                ci = c
                err = "The variable name {0} is used in columns {1} and {2} in the Excel sheet..\n".format(cell, si, ci)
                seterrorstring(geterrorstring() + err)
                return EC.DulpicateVariable
            varheader.append(cell)

        # second calculate the number of rows.
        rows = worksheet.nrows

        # read all variable list
        for c in range(cols):
            cell = worksheet.cell(0, c).value.strip()
            if cell == '':
                break

            valuelist = []
            for r in range(1, rows):
                cell = worksheet.cell(r, c).value
                if isinstance(cell, float):
                    if cell - int(cell) == 0:
                        cell = str(int(cell))
                    else:
                        cell = str(cell)
                if isinstance(cell, int):
                    cell = str(cell)
                valuelist.append(cell)
            convmap[varheader[c]] = valuelist

    except XLRDError:
        return EC.InvalidExcel
    else:
        return EC.OK
    pass

def orderupdate(filename, fieldname):
    df = pd.read_excel(filename, sheet_name=0)
    df = df.sort_values(by=fieldname)

    writer = pd.ExcelWriter('uploads/reordered.xlsx')
    df.to_excel(writer, index=False)
    writer.save()

    configmap('uploads/reordered.xlsx')

# def concatStart(excelfile, code_col, department_col):
#     df_tde = pd.read_excel(excelfile, dtype={code_col:str})
#     # df_tde[code_col] = df_tde[code_col].astype(str)
#     # df_tde[code_col] = df_tde[code_col].apply('="{}"'.format)

#     df_sample = pd.read_excel("codes département.xlsx", dtype={"$code-departement":str})
    
def get_codeSample():
    result = {}
    df_sample = pd.read_excel(StaticFile_PATH + "codes département.xlsx", dtype={"$code-departement":str})
    for index, row in df_sample.iterrows():
        result[row['$code-departement']] = row['$nom-departement']
    return result

def concatStart(excelfile, code_col, department_col):   

    new_convmap = convmap

    department_col_list = []
    
    result = EC.OK

    code_sample = get_codeSample()

    # number of rows
    total_rows = len(new_convmap[code_col])
    for row_index in range(total_rows):
        code_val = new_convmap[code_col][row_index].strip()

        department_val = ""

        if len(code_val) >= 2:
            first_two = code_val[:2]
            if first_two in code_sample.keys():
                department_val = code_sample[first_two]
        if len(code_val) >= 3:
            first_3 = code_val[:3]
            if first_3 in code_sample.keys():
                department_val = code_sample[first_3]
        department_col_list.append(department_val)

    new_convmap[department_col] = department_col_list

    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('sheet1')

    for col_index, value in enumerate(new_convmap.keys()):
        sheet.write(0, col_index, value)

        for row_index, row_val in enumerate(new_convmap[value]):
            sheet.write(row_index + 1, col_index, row_val)


     # last zip result files.
    tz_paris = pytz.timezone('Europe/Paris')
    now = datetime.now(tz_paris)

    result_file_name = 'add-department' + '-' + '{:02d}'.format(now.day) + "-" + '{:02d}'.format(now.month) + "-" + str(
            now.year) + "-" + '{:02d}'.format(now.hour) + "h" + '{:02d}'.format(now.minute) + ".xls"

    file_root = "static/result/" + result_file_name
    
    workbook.save(file_root)

    set_download_root(file_root)
    return result

def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except (TypeError, NameError): # unicode is a default on python 3 
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)



