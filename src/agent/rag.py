import chromadb


class KnowledgeBase:
    def __init__(self):
        client = chromadb.Client()
        self.collection = client.create_collection("buildcraft")


    def add(self, doc_id: str, text: str) -> None:
        # TODO: add `text` to the collection with id=doc_id
        self.collection.add(documents=[text], ids=[doc_id])

    def query(self, text: str, n: int = 3) -> list[str]:
        # TODO: query the collection with query_texts=[text], n_results=n
        # TODO: return results["documents"][0]
        results = self.collection.query(query_texts=[text], n_results=n)
        return results["documents"][0]
