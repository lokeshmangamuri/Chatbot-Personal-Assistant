from docling.document_converter import DocumentConverter
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DataLoader:

    def __init__(self, pdf_path):

        self.pdf_path = pdf_path

    def load(self):

        converter = DocumentConverter()
        result = converter.convert(self.pdf_path)

        markdown = result.document.export_to_markdown()

        document = Document(
            page_content=markdown,
            metadata={"source": self.pdf_path})

        return [document]

    def split_documents(self, documents):

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
        )

        chunks = splitter.split_documents(documents)

        print(f"Number of chunks: {len(chunks)}")

        return chunks