from jina import Executor, DocumentArray, requests
from docarray import Document
import requests as rq  # bc we also need requests decorator from jina
import json

"""
  Python script to upload a PDF to the function called by https://docs2info.com/demo.

  This script has been tested with Python 3.8.5 on a Mac.

  Please send problem reports and other feedback to john@docs2info.com
"""

HOST = "https://pdftables-2uqbalu5ya-uw.a.run.app/"
URL = HOST + "upload"
MIN_WIDTH = 2  # Minimum table width
MIN_HEIGHT = 2  # Minimum table height


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
    multiple_files = [("uploaded-file", (path, open(path, "rb"), "application/pdf"))]
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
    for k in ("NumberPages", "FirstPageProcessed", "LastPageProcessed"):
        val2int(doc, k)
    for k in list(doc["PageTables"].keys()):
        key2int(doc["PageTables"], k)
    for k in list(doc["PageTables"].keys()):
        for i in range(len(doc["PageTables"][k])):
            val2int(doc["PageTables"][k][i], "Width")
            val2int(doc["PageTables"][k][i], "Height")
    return doc


def get_csv_data(doc, min_width, min_height):
    """
    min_width is the minimum table width.
    min_height is the minimum table height.
    """
    table_data = []
    doc_tables = doc["PageTables"]
    for page_num in sorted(doc_tables.keys()):
        print(page_num)
        page_tables = doc_tables[page_num]
        table_num = 1
        for table in page_tables:
            width = table["Width"]
            height = table["Height"]
            if width < min_width or height < min_height:
                continue
            # out_path = f'{out_root}.page{page_num:03d}.table{table_num:03d}.csv'
            data = table["Data"]
            table_data.append(data)
            table_num += 1

    return table_data


class PDFTableExtractor(Executor):
    @requests
    def extract_tables(self, docs, **kwargs):
            for doc in docs:
                text = uploadPDF(doc.uri)
                json_doc = jsonToDoc(text)
                table_data = get_csv_data(json_doc, MIN_WIDTH, MIN_HEIGHT)
                
                for table in table_data:     
                    doc.chunks.append(Document(text=table_data))
