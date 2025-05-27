import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import numpy as np
import pandas as pd
from rapidfuzz import fuzz
try:
    import easyocr
    OCR_ENGINE = 'easyocr'
except ImportError:
    import pytesseract
    OCR_ENGINE = 'pytesseract'


def preprocess_image(image_path):
    """Load image and perform preprocessing for OCR."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError('Could not read image: %s' % image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


def extract_names_from_image(image):
    """Run OCR on the preprocessed image and return a list of names."""
    if OCR_ENGINE == 'easyocr':
        reader = easyocr.Reader(['en'])
        result = reader.readtext(image, detail=0)
        text = ' '.join(result)
    else:
        text = pytesseract.image_to_string(image)
    raw_names = [n.strip() for line in text.splitlines() for n in line.split(',')]
    names = [n for n in raw_names if n]
    return names


def compare_names(ocr_names, reference_names, threshold=80):
    """Compare OCR names against reference names using fuzzy matching."""
    results = []
    for ref in reference_names:
        best_score = 0
        best_match = ''
        for ocr in ocr_names:
            score = fuzz.ratio(ref.lower(), ocr.lower())
            if score > best_score:
                best_score = score
                best_match = ocr
        found = best_score >= threshold
        results.append({'Name': ref, 'Found': 'Yes' if found else 'No', 'OCR Match': best_match})
    return results


class NameCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Name Checker')
        self.image_path = None
        self.current_results = []
        self.setup_ui()

    def setup_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill='both', expand=True)
        tk.Label(frame, text='Reference Names (one per line or comma separated):').pack(anchor='w')
        self.names_text = tk.Text(frame, height=10)
        self.names_text.pack(fill='both', expand=True)
        self.upload_btn = tk.Button(frame, text='Upload Ribbon Image', command=self.upload_image)
        self.upload_btn.pack(pady=5)
        self.check_btn = tk.Button(frame, text='Run Check', command=self.run_check)
        self.check_btn.pack(pady=5)
        self.tree = ttk.Treeview(frame, columns=('Name','Found','OCR Match'), show='headings')
        for col in ('Name','Found','OCR Match'):
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True, pady=5)
        self.save_btn = tk.Button(frame, text='Save Results', command=self.save_results)
        self.save_btn.pack(pady=5)

    def upload_image(self):
        path = filedialog.askopenfilename(title='Select ribbon image', filetypes=[('Image Files','*.png;*.jpg;*.jpeg;*.bmp')])
        if path:
            self.image_path = path
            messagebox.showinfo('Image Selected', f'Image loaded: {path}')

    def run_check(self):
        if not self.image_path:
            messagebox.showerror('No Image', 'Please upload an image first.')
            return
        names_input = self.names_text.get('1.0', tk.END)
        reference_names = [n.strip() for line in names_input.splitlines() for n in line.split(',') if n.strip()]
        if not reference_names:
            messagebox.showerror('No Names', 'Please enter reference names.')
            return
        try:
            preprocessed = preprocess_image(self.image_path)
            ocr_names = extract_names_from_image(preprocessed)
            results = compare_names(ocr_names, reference_names)
            self.update_results_table(results)
            self.current_results = results
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def update_results_table(self, results):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for res in results:
            self.tree.insert("", "end", values=(res["Name"], res["Found"], res["OCR Match"]))

    def save_results(self):
        if not self.current_results:
            messagebox.showerror('No Results', 'No results to save.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV Files','*.csv')])
        if path:
            df = pd.DataFrame(self.current_results)
            df.to_csv(path, index=False)
            messagebox.showinfo('Saved', f'Results saved to {path}')


def main():
    root = tk.Tk()
    app = NameCheckerApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
