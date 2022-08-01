import requests as rq  # bc we also need requests decorator from jina
import json
import sys
import csv
import os
import shutil

HOST = 'https://pdftables-2uqbalu5ya-uw.a.run.app/'
URL = HOST + 'upload'
OUT_DIR = 'extracted.tables'
MIN_WIDTH = 2 # Minimum table width
MIN_HEIGHT = 2 # Minimum table height

def uploadPDF(path):
  """
    uploadPDF uploads the PDF in path to a table extraction API and returns a dict of extracted
	data as a JSON string.

    The returned JSON dict has keys
      'NumberPages': Number of pages in PDF.
      'FirstPageProcessed': First page of PDF processed (1 - 'NumberPages').
      'LastPageProcessed': Las page of PDF processed (1 - 'NumberPages').
      'PageTables': The tables found.
    jsonToDoc below converts the JSON to a python dict.
  """
  multiple_files = [('uploaded-file', (path, open(path, 'rb'), 'application/pdf'))]
  # r = requests.post(URL, files=multiple_files)
  r = rq.post(URL, files=multiple_files)

  if r.status_code != 200:
    print(f"uploadPDF failed. r={r}")
    return None
  return r.text


def key2int(d, k):
  """
    key2int converts key k in dict d to an int.
  """
  d[int(k)] = d[k]
  del d[k]

def val2int(d, k):
  """
    val2int converts d[k] to an int.
  """
  d[k] = int(d[k])


def jsonToDoc(text):
  """
    jsonToDoc converts json string text to a dict describing extracted tables.
  """
  doc = json.loads(text)
  for k in ('NumberPages', 'FirstPageProcessed', 'LastPageProcessed'):
    val2int(doc, k)
  for k in list(doc['PageTables'].keys()):
    key2int(doc['PageTables'], k)
  for k in list(doc['PageTables'].keys()):
    for i in range(len(doc['PageTables'][k])):
      val2int(doc['PageTables'][k][i], 'Width')
      val2int(doc['PageTables'][k][i], 'Height')
  return doc

def makeOutRoot(out_dir, in_path):
   """
     makeOutRoot returns a path in directory out_dir with same base name as in_path.
   """
   name = os.path.basename(in_path)
   name, _ = os.path.splitext(name)
   return os.path.join(out_dir, name)


def writeCsvs(out_root, doc, min_width, min_height):
  """
    writeCsvs writes the tables in dict doc to CSV files with names starting with out_root.
    min_width is the minimum table width.
    min_height is the minimum table height.
  """
  doc_tables = doc['PageTables']
  for page_num in sorted(doc_tables.keys()):
    page_tables = doc_tables[page_num]
    table_num = 1
    for table in page_tables:
      width = table['Width']
      height = table['Height']
      if width < min_width or height < min_height:
       continue
      out_path = f'{out_root}/page{page_num:03d}.table{table_num:03d}.csv'
      data = table['Data']
      with open(out_path, 'w') as f:
        writer = csv.writer(f)
        for row in data:
          writer.writerow(row)
      # print(f"Wrote a {width:2d} x {height:2d} table to '{out_path}'")
      table_num += 1
