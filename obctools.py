import re
import xml.etree.ElementTree as etree
import os
import platform
import subprocess

def prepare_speech(sn):
    speech = etree.tostring(sn).decode("utf-8")
    speechend = speech.find('</speech>')
    speech = speech[:speechend] + "</speech>"
    speech = strip_xml_tags(speech, 'speech')
    speech = speech.replace("\n"," ")
    return speech

def get_periods(y,n):
    try:
        y = int(y)    
    except Exception as e:
        print(y,e)
    p = ""
    if n == 2:
        if y <= 1816:
            p = "1720-1816"
        else:
            p = "1817-1913"
    elif n == 3:
        if y <= 1784:
            p = "1720-1784"
        elif y <= 1849:
            p = "1785-1849"
        else:
            p = "1850-1913"
    elif n == 4:
        if y <= 1768:
            p = "1720-1768"
        elif y <= 1817:
            p = "1769-1817"
        elif y <= 1865:
            p = "1818-1865"
        else:
            p = "1866-1913"
    elif n == 5:
        if y <= 1758:
            p = "1720-1758"
        elif y <= 1797:
            p = "1759-1797"
        elif y <= 1836:
            p = "1798-1836"
        elif y <= 1875:
            p = "1837-1875"
        else:
            p = "1876-1913"
    elif n == 6:
        if y <= 1752:
            p = "1720-1752"
        elif y <= 1785:
            p = "1753-1785"
        elif y <= 1817:
            p = "1786-1817"
        elif y <= 1849:
            p = "1818-1849"
        elif y <= 1881:
            p = "1850-1881"
        else:
            p = "1882-1913"
    return p

def strip_pos_tags(s):
    s = re.sub(r'_[^\s]+', r'', s)
    return s


def get_wc_from_string(s):
    wc = 0
    words = re.split('[^0-9A-Za-z\-\']+', s)
    words = [_f for _f in words if _f]
    wc = len(words)
    return wc


def convert_listbox_to_list(lb, which=""):
    sel = lb.curselection()
    res = []
    for s in sel:
        r = lb.get(s)
        if which=="gender":
            r =r[0]
        if which=="role":
            r = r.replace("unknown","u")
        if which=="hisclass":
            r = r.replace("unknown","u")
            dash_pos = r.find(" - ")
            r = r[:dash_pos]
        res.append(r)
    return res


def make_dir(a_path):
    """ makes sure directory exists, creating it if necessary"""
    try:
        os.makedirs(a_path)
        return True
    except Exception as e:
        if os.path.exists(a_path):
            return True
        else:
            print("Could not create directory.")
            print(e)
            return False


def convert_hisclass_to_binclass(hisclass):
    binclass = ""
    if hisclass in ['1', '2', '3', '4', '5']:
        binclass = 'higher (1-5)'
    if hisclass in ['6', '7', '8', '9', '10', '11', '12', '11/12', '13']:
        binclass = 'lower (6-13)'
    return binclass


def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def open_file_externally(csv_path):
    if platform.system() == "Windows":
        os.startfile(csv_path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", csv_path])
    else:
        subprocess.Popen(["xdg-open", csv_path])


def strip_xml_tags(s, tag=None):
    if tag:
        t = '<[/]?' + tag + '[\s\S]*?>'
        s = re.sub(t, '', s)
    else:
        s = re.sub(r'<[\s\S]*?>', r'', s)
    return s
