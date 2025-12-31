from utils.logger import get_logger 
from db.connections import get_guident_db
from typing import Optional
from utils.document_type import get_document_type_from_filename
import uuid
logger= get_logger(__name__)
def insert_document_to_database(work_id: str, file_name: str, file_size: int,
                                content_type: str, s3_url: str) -> Optional[str]:
    """Insert document metadata."""
    conn = None
    logger.info(f"Inserting document for work_id={work_id}, file_name={file_name}")
    try:
        conn = get_guident_db()
        cursor = conn.cursor()
        
        document_type = get_document_type_from_filename(file_name)
        
        insert_query = """
            INSERT INTO invoice_documents
            (document_id, work_id, file_name, file_size, document_type,
             is_primary, s3_url, ocr_status, uploaded_at)
            VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """
        
        document_id = str(uuid.uuid4())
        is_primary = (document_type == 'INVOICE' and 'pdf' in content_type.lower())
        logger.debug(f"Generated document_id={document_id}, is_primary={is_primary}")
        cursor.execute(insert_query, (
            document_id, work_id, file_name, file_size,
            document_type, is_primary, s3_url, 'PENDING'
        ))
        
        conn.commit()
        cursor.close()
        logger.info(f"Document inserted successfully: {file_name} (document_id={document_id})")
        
        return document_id
        
    except Exception as e:
        logger.error(f"Error inserting document for work_id={work_id}, file_name={file_name}: {str(e)}", exc_info=True)
        if conn:
            conn.rollback()
            logger.debug("Database transaction rolled back due to error.")
        return None
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed.")
