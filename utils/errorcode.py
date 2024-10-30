from enum import IntEnum

errorstring = ""

class ErrorCode(IntEnum):
    OK = 0
    InvalidExcel = 1
    InvalidZip = 2
    NoExistZip = 3
    NoExistExcel = 4
    EmptyFileName = 5
    UnZipFail = 6
    InvalidTxt = 7
    DulpicateVariable = 8
    NoExistVariable = 9

    ParagraphsNotSame = 10

    NoPairedtags = 11
    NoExistVariable_and_NoPairedtags = 12

def geterrorstring():
    return errorstring


def seterrorstring(err):
    global errorstring
    errorstring = err



