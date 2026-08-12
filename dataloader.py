from docling.document_converter import DocumentConverter
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DataLoader:

    def __init__(self):

        self.converter = DocumentConverter()

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
        )


    def load(self, source):

        result = self.converter.convert(source)

        markdown = result.document.export_to_markdown()

        document = Document(
            page_content=markdown,
            metadata={
                "source": str(source)
            }
        )

        return [document]


    def split_documents(self, documents):

        chunks = self.splitter.split_documents(documents)

        print(f"Number of chunks: {len(chunks)}")

        return chunks