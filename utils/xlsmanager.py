from xlrd import open_workbook, XLRDError
from utils.errorcode import ErrorCode as EC
from utils.errorcode import geterrorstring
from utils.errorcode import seterrorstring

import pandas as pd



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

