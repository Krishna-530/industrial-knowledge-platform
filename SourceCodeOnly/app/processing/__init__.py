"""Processing module initialization"""
from app.processing.factory import processor_factory
from app.processing.processors.txt_processor import TxtProcessor
from app.processing.processors.markdown_processor import MarkdownProcessor
from app.processing.processors.pdf_processor import PdfProcessor
from app.processing.processors.docx_processor import DocxProcessor
from app.processing.processors.pptx_processor import PptxProcessor

# Register processors
processor_factory.register("text/plain", TxtProcessor())
processor_factory.register("text/markdown", MarkdownProcessor())
processor_factory.register("text/x-markdown", MarkdownProcessor())
processor_factory.register("application/pdf", PdfProcessor())
processor_factory.register("application/vnd.openxmlformats-officedocument.wordprocessingml.document", DocxProcessor())
processor_factory.register("application/vnd.openxmlformats-officedocument.presentationml.presentation", PptxProcessor())
