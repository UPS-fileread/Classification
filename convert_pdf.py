import fitz
import os

def pdf_to_text(pdf_bytes, num_pages=5):
    """
    Convert the first num_pages of a PDF (from bytes) to text.
    Returns the extracted text as a string.
    """
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        pages_to_use = doc[:num_pages]
        text = "\n\n".join(page.get_text() for page in pages_to_use)
    return text

# The following is the original batch script, kept for reference.
# Settings
# input_dir = "data/Litigation/Motion" 
# output_dir = "output/Litigation/Motion"  
# num_pages = 5  
# os.makedirs(output_dir, exist_ok=True)
# for filename in os.listdir(input_dir):
#     if not filename.lower().endswith(".pdf"):
#         continue
#     input_path = os.path.join(input_dir, filename)
#     doc = fitz.open(input_path)
#     pages_to_use = doc[:num_pages]
#     text = "\n\n".join(page.get_text() for page in pages_to_use)
#     base = os.path.splitext(filename)[0]
#     out_filename = f"{base}_first{len(pages_to_use)}pages.txt"
#     out_path = os.path.join(output_dir, out_filename)
#     with open(out_path, "w", encoding="utf-8") as f:
#         f.write(text)
#     print(f"Saved: {out_path}")