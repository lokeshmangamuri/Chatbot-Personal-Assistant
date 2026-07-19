from langchain_core.documents import Document
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper


class WebSearcher:

    def __init__(self):
        self.wrapper = DuckDuckGoSearchAPIWrapper()

    def search(self, query, k=5):

        results = self.wrapper.results(query, max_results=k)
        documents = []

        for result in results:

            documents.append(Document(
                    page_content=result["snippet"],
                    metadata={"title": result["title"],
                        "url": result["link"],
                        "source": "web"}))
        return documents
