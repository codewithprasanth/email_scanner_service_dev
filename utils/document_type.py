from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

# Allowed extensions -> document_type
MIME_EXTENSION_TO_DOC_TYPE = {
    '.pdf': 'pdf',
    '.pdfa': 'pdfa',
    '.jpg': 'jpg',
    '.jpeg': 'jpeg',
    '.png': 'png',
    '.tiff': 'tiff',
    '.tif': 'tif',
    '.bmp': 'bmp',
    '.gif': 'gif',
    '.pcx': 'pcx'
}
 

def get_document_type_from_filename(filename) -> str:
    """
    Determine document_type based on file extension.
    Only allowed types are returned; unsupported types raise an error.
    """
    ext = Path(filename).suffix.lower()
    if ext in MIME_EXTENSION_TO_DOC_TYPE:
        doc_type = MIME_EXTENSION_TO_DOC_TYPE[ext]
        logger.info(f"File '{filename}' mapped to document_type='{doc_type}'")
        return doc_type
    else:
        logger.error(f"Unsupported file extension '{ext}' for file '{filename}'")
        raise ValueError(f"Unsupported document type: '{ext}'")

 