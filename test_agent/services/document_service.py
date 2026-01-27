from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import DocumentStream
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter
import hashlib
from typing import Union
from io import BytesIO
from uuid import UUID

from test_agent.db.repositories.document import create_document, create_document_chunks

doc_converter = DocumentConverter()


def _convert_to_markdown(file_content: bytes) -> str:
    try:
        pdf_file = BytesIO(file_content)
        pdf_file.name = "sample.pdf"
        doc = DocumentStream(name=pdf_file.name, stream=pdf_file)
        result = doc_converter.convert(source=doc)
        markdown = result.document.export_to_markdown()
    except Exception:
        raise ValueError(
            "Failed to extract PDF content for the files passed. Please check the file uploaded"
        )
    return markdown


def _generate_hash(content: Union[bytes, str]) -> str:
    if type(content) == str:
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def _chunk_markdown_document(file_content: str) -> list[Document]:
    text_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")],
        strip_headers=False,
    )
    return text_splitter.split_text(text=file_content)


def ingest_document(
    project_id: UUID,
    release_id: UUID,
    document: bytes,
    document_type: str,
    document_status: str,
):

    document_hash = _generate_hash(document)
    markdown_content = _convert_to_markdown(document)
    document_id = create_document(
        project_id=project_id,
        document_type=document_type,
        content=markdown_content,
        document_hash=document_hash,
        document_status=document_status,
        release_id=release_id,
    )
    chunks = [
        chunk.page_content for chunk in _chunk_markdown_document(markdown_content)
    ]
    create_document_chunks(document_id, chunks)
