# PDFTableExtractor

This Executor uses docs2info's [Table Extraction service](https://docs2info.com/services/tables/) to extract tables from PDF files and store them as chunks. The format of each chunk is simply the string of a CSV saved in `chunk.text` so it can be parsed by an encoder and then displayed in a front-end by rendering a CSV as table in the interface.

If anyone has a better idea of how to store tabular data in a way that can still be recognized by an encoder, drop an issue in the [repo](https://github.com/alexcg1/executor-pdf-table-extractor/issues).

## 🚨🚨 IMPORTANT WARNING 🚨🚨

Do not use this with confidential or sensitive documents. The table extraction service is still under heavy development and they use uploaded PDFs for training their model. 

## License

The code is adapted from [`extract_tables.py`](https://docs2info.com/extract_tables.py) with the kind permission of the [author](https://twitter.com/docs2info). No license is specified.
