import requests as rq  # bc we also need requests decorator from jina
import os
from docarray import DocumentArray
from executor import PDFTableExtractor

urls = ["https://arxiv.org/pdf/2203.09974.pdf"]
data_dir = "data"

if not os.path.isdir(data_dir):
    os.makedirs(data_dir)

for url in urls:
    filename = f"{data_dir}/{url.split('/')[-1]}"
    r = rq.get(url, allow_redirects=True)

    with open(filename, "wb") as file:
        file.write(r.content)

docs = DocumentArray.from_files("data/*.pdf")

ex = PDFTableExtractor()
ex.extract_tables(docs)

print(docs[0].chunks)

from pprint import pprint

for chunk in docs[0].chunks:
    pprint(chunk.text)
