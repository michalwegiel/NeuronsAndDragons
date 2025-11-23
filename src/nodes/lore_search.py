from langchain.tools import tool

from data.lore.lore_storage import get_vector_store


retriever = get_vector_store().as_retriever(search_type="similarity", search_kwargs={"k": 1})


@tool
def lore_search(query: str) -> str:
    """Search the stored RPG lore using semantic embedding search."""
    results = retriever.invoke(query)
    return "\n\n".join([r.page_content for r in results])
