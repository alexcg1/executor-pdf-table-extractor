from jina import Executor, DocumentArray, requests
from docarray import Document
import requests as rq  # bc we also need requests decorator from jina
import json
from glob import glob
from table_extractor_code import *

class TableExtractor(Executor):
    @requests
    def extract_tables(self, docs, **kwargs):
        for doc in docs:
            # make temp dir
            out_root = "extracted.tables"
            os.makedirs(out_root, exist_ok=True)

            # extract tables
            # print(doc.uri)
            text=uploadPDF(doc.uri)
            converted_pdf = jsonToDoc(text)
            writeCsvs(out_root, converted_pdf, MIN_WIDTH, MIN_HEIGHT)

            # put tables in docarray
            tables = DocumentArray()
            csvs = glob(f"{out_root}/*.csv")

            for csv_file in csvs:
                with open(csv_file, "r") as file:
                    table_doc = Document(text=file.read())
                    tables.append(table_doc)

            # store as chunks
            doc.chunks = tables

            shutil.rmtree(out_root)