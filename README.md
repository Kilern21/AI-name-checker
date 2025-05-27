# AI Name Checker

This application provides a simple GUI for matching names printed on a ribbon to a reference list. It uses OCR to extract text from an uploaded image and compares the extracted names against user provided names with fuzzy matching.

## Requirements
Install dependencies with:

```bash
pip install -r requirements.txt
```

Either `easyocr` or `pytesseract` will be used for OCR depending on which is installed.

## Running
On Windows, run `start.bat` or execute:

```bash
python name_checker_app.py
```

The GUI allows you to enter reference names, upload an image of a ribbon, run the check, and save the results to CSV.
