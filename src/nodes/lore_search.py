from typing import Annotated

from data.lore.lore_storage import get_vector_store


retriever = get_vector_store().as_retriever(search_type="similarity", search_kwargs={"k": 3})


def lore_search(query: Annotated[str, "Search query for setting lore (places, items, history, etc.)"]) -> str:
    """Search the stored RPG lore using semantic embedding search."""
    results = retriever.invoke(query)
    serialized = "\n\n".join(f"Source: {doc.metadata}\nContent: {doc.page_content}" for doc in results)
    return serialized
