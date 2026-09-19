import os
import json
import faiss
from sentence_transformers import SentenceTransformer


# Project folders
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DOCUMENTS_DIR = os.path.join(
    BASE_DIR,
    "knowledge_base",
    "documents"
)

VECTOR_STORE_DIR = os.path.join(
    BASE_DIR,
    "rag",
    "vector_store"
)


# Create vector store folder if it doesn't exist
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)


# Load embedding model
print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded!")


# Store document chunks
chunks = []


# Read all text files
for filename in os.listdir(DOCUMENTS_DIR):

    if filename.endswith(".txt"):

        file_path = os.path.join(DOCUMENTS_DIR, filename)

        print(f"Reading: {filename}")

        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

        # Split document into paragraphs
        paragraphs = text.split("\n\n")

        for paragraph in paragraphs:

            paragraph = paragraph.strip()

            if paragraph:

                chunks.append({
                    "text": paragraph,
                    "source": filename
                })


print(f"Total chunks created: {len(chunks)}")


# Extract text for embedding
texts = [chunk["text"] for chunk in chunks]


# Generate embeddings
print("Creating embeddings...")

embeddings = model.encode(
    texts,
    convert_to_numpy=True
)


# Create FAISS index
dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)


# Save FAISS index
index_path = os.path.join(
    VECTOR_STORE_DIR,
    "knowledge.index"
)

faiss.write_index(index, index_path)


# Save chunks and source information
chunks_path = os.path.join(
    VECTOR_STORE_DIR,
    "chunks.json"
)

with open(chunks_path, "w", encoding="utf-8") as file:

    json.dump(
        chunks,
        file,
        indent=4,
        ensure_ascii=False
    )


print()
print("===================================")
print("RAG KNOWLEDGE BASE CREATED!")
print("===================================")
print(f"FAISS index: {index_path}")
print(f"Chunks file: {chunks_path}")
print(f"Total chunks: {len(chunks)}")