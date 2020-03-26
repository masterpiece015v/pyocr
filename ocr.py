from PIL import Image
import sys
import pyocr
import pyocr.builders
import os
import glob
from urllib.parse import urlparse
import mysql.connector

tools = pyocr.get_available_tools()

if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)

tool = tools[0]
#print("Will use tool '%s'" % (tool.get_name()))
langs = tool.get_available_languages()
#print("Available languages: %s" % ", ".join(langs))
lang = langs[2]
#print("Will use lang '%s'" % (lang))
path_files = glob.glob('C:\\Users\\watabe\\Google ドライブ\\国家試験問題作成\\question\\feh*.png')
#print( path_files )

url = urlparse("mysql://webmaster:P@ssword@192.168.11.20:3306/examsitedb")

conn = mysql.connector.connect(
    host = url.hostname,
    port = url.port,
    user = url.username,
    password = url.password,
    database = url.path[1:]
)

print( conn.is_connected())

cur = conn.cursor(prepared=True)

for path_file in path_files:
    txt = tool.image_to_string(
        Image.open( path_file ),lang=lang,builder=pyocr.builders.TextBuilder()
    )
    name_file = path_file.split("\\")
    q_id = name_file[len(name_file) - 1].split(".")[0]
    q_content = txt.replace("\n","")
    q_content = q_content.replace(" ","")
    print( q_id )
    print( q_content )

    try:
        cur.execute("update exam_question set q_content=? where q_id=?",(q_content,q_id))
        conn.commit()
        print( "commit")
    except:
        conn.rollback()
        print( "rollback")
        raise

cur.close()
conn.close()
