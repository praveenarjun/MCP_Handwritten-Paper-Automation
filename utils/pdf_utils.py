import fitz  # PyMuPDF
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

def pdf_to_images(pdf_path, zoom_x=2.0, zoom_y=2.0):
    """
    Converts a PDF file into a list of PIL Images.
    Args:
        pdf_path (str): Path to the PDF file.
        zoom_x (float): Horizontal zoom factor for higher resolution.
        zoom_y (float): Vertical zoom factor.
    Returns:
        list[PIL.Image]: List of images, one per page.
    """
    images = []
    try:
        doc = fitz.open(pdf_path)
        mat = fitz.Matrix(zoom_x, zoom_y)
        for page in doc:
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            images.append(img)
        doc.close()
        return images
    except Exception as e:
        logger.error(f"Error converting PDF to images: {e}")
        return []

def extract_pdf_text(pdf_path):
    """
    Extracts text from a digital PDF file.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        str: Extracted text joined by newlines.
    """
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""
