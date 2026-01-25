from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import DocumentStream
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter
from test_agent import config
import hashlib
from typing import Union
from io import BytesIO

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


def generate_hash(content: Union[bytes, str]) -> str:
    if type(content) == str:
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def process_document(file: bytes) -> tuple[str, str]:

    document_hash_id = generate_hash(content=file)
    markdown_content = _convert_to_markdown(file)
    return document_hash_id, markdown_content


def chunk_markdown_document(file_content: str) -> list[str]:
    text_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")],
        strip_headers=False,
    )
    return text_splitter.split_text(text=file_content)
