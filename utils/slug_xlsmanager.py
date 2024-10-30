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

def concatStart(data):
    excelfile = data['xls']
    concat_1 = data['concat_1']
    concat_2 = data['concat_2']
    concat_3 = data['concat_3']
    concat_4 = data['concat_4']

    use_prefix = data['use_prefix']
    prefix = data['prefix']
    beginSlash = data['beginSlash']
    tailSlash = data['tailSlash']

    new_convmap = convmap
    result = EC.OK

    # number of rows
    total_rows = len(new_convmap[concat_1])
    for row_index in range(total_rows):
        concat_1_val = new_convmap[concat_1][row_index].strip()
        concat_2_val = new_convmap[concat_2][row_index].strip()
        concat_3_val = ''
        if concat_3 != '':
            concat_3_val = new_convmap[concat_3][row_index].strip()

        concat_list = []
        if concat_1_val != '':
            concat_list.append(concat_1_val)
        if concat_2_val != '':
            concat_list.append(concat_2_val)
        if concat_3_val != '':
            concat_list.append(concat_3_val)

        new_val = '-'.join(concat_list)

        if use_prefix == True:
            new_val = prefix + new_val
        if beginSlash == True:
            new_val = '/' + new_val
        if tailSlash == True:
            new_val = new_val + '/'

        new_val = strip_accents(new_val)
        new_val = new_val.replace("'", " ")

        # replace multiple spaces with one space
        re.sub(' +', ' ', new_val)

        new_val = new_val.replace(' ', '-')
        new_val = new_val.lower()

        new_convmap[concat_4][row_index] = new_val

    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('sheet1')

    for col_index, value in enumerate(new_convmap.keys()):
        sheet.write(0, col_index, value)

        for row_index, row_val in enumerate(new_convmap[value]):
            sheet.write(row_index + 1, col_index, row_val)


     # last zip result files.
    tz_paris = pytz.timezone('Europe/Paris')
    now = datetime.now(tz_paris)

    result_file_name = 'output' + '-' + '{:02d}'.format(now.day) + "-" + '{:02d}'.format(now.month) + "-" + str(
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