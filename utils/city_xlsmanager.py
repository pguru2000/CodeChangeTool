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


UPLOAD_PATH = 'uploads/slug_generator/'
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

def concatStart(excelfile, city_col, concat_col_list, population_col):
    new_convmap = convmap
    result = EC.OK

    # number of rows
    total_rows = len(new_convmap[city_col])

    result_dic = {}
    population_dic = {}
    for row_index in range(total_rows):
        city_val = new_convmap[city_col][row_index].strip()
        result_dic[city_val] = 0

        if population_col != '':
            population_dic[city_val] = new_convmap[population_col][row_index].strip()

    for city_name in result_dic.keys():



        for row_index in range(total_rows):
            for concat_col in concat_col_list:
                concat_val = new_convmap[concat_col][row_index].strip()

                if city_name == concat_val:

                    result_dic[city_name]  += 1

    result_dic = dict(sorted( result_dic.items(), key=lambda item: item[1]))

    print(result_dic)



    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('sheet1')

    index = 0
    for key, value in result_dic.items():
        sheet.write(index, 0, key)
        sheet.write(index, 1, value)
        if population_col != '':
            sheet.write(index, 2, population_dic[key])

        index += 1

    print(population_col)
    print(population_dic)

     # last zip result files.
    tz_paris = pytz.timezone('Europe/Paris')
    now = datetime.now(tz_paris)

    result_file_name = 'city_occurences_output' + '-' + '{:02d}'.format(now.day) + "-" + '{:02d}'.format(now.month) + "-" + str(
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



