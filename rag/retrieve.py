import os
import json
import re

import faiss
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VECTOR_STORE_DIR = os.path.join(
    BASE_DIR,
    "rag",
    "vector_store"
)

INDEX_FILE = os.path.join(
    VECTOR_STORE_DIR,
    "knowledge.index"
)

CHUNKS_FILE = os.path.join(
    VECTOR_STORE_DIR,
    "chunks.json"
)


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding model loaded!")


# ============================================================
# LOAD FAISS INDEX
# ============================================================

print("Loading FAISS knowledge index...")

if not os.path.exists(INDEX_FILE):
    raise FileNotFoundError(
        f"FAISS index not found: {INDEX_FILE}"
    )

index = faiss.read_index(INDEX_FILE)

print("FAISS index loaded!")


# ============================================================
# LOAD KNOWLEDGE CHUNKS
# ============================================================

if not os.path.exists(CHUNKS_FILE):
    raise FileNotFoundError(
        f"Chunks file not found: {CHUNKS_FILE}"
    )

with open(
    CHUNKS_FILE,
    "r",
    encoding="utf-8"
) as file:

    chunks = json.load(file)

print(
    f"Knowledge chunks loaded: {len(chunks)}"
)


# ============================================================
# KEYWORD GROUPS
# ============================================================

SCIENTIFIC_REFERENCE_KEYWORDS = [
    "scientific reference",
    "scientific evidence",
    "study",
    "research",
    "source",
    "faO",
    "fao",
    "recarbonizing",
    "conservation agriculture",
    "soil organic cover",
    "soil biodiversity",
    "water holding capacity"
]

SOIL_KEYWORDS = [
    "soil",
    "soil organic carbon",
    "organic carbon",
    "soc",
    "soil health",
    "soil structure",
    "soil biodiversity",
    "soil moisture",
    "water infiltration"
]

BIODIVERSITY_KEYWORDS = [
    "biodiversity",
    "species richness",
    "habitat diversity",
    "habitat",
    "species",
    "connectivity",
    "fragmentation"
]

CLIMATE_KEYWORDS = [
    "rainfall",
    "temperature",
    "drought",
    "water",
    "moisture",
    "climate",
    "water availability"
]

LAND_USE_KEYWORDS = [
    "land use",
    "land-use",
    "monoculture",
    "intercropping",
    "crop rotation",
    "agroforestry",
    "cropping",
    "vegetation",
    "agriculture"
]


# ============================================================
# HELPER: NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    if text is None:
        return ""

    text = str(text).lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# HELPER: CHECK KEYWORDS
# ============================================================

def keyword_score(query, chunk_text):

    query_text = normalize_text(query)

    chunk_text = normalize_text(chunk_text)

    score = 0

    keyword_groups = [
        SOIL_KEYWORDS,
        BIODIVERSITY_KEYWORDS,
        CLIMATE_KEYWORDS,
        LAND_USE_KEYWORDS
    ]

    for group in keyword_groups:

        for keyword in group:

            if keyword in query_text and keyword in chunk_text:

                # Stronger score for exact scientific terms
                if len(keyword.split()) > 1:
                    score += 3
                else:
                    score += 1

    return score


# ============================================================
# HELPER: SOURCE BONUS
# ============================================================

def source_bonus(query, chunk):

    query_text = normalize_text(query)

    source_name = normalize_text(
        chunk.get("source", "")
    )

    chunk_text = normalize_text(
        chunk.get("text", "")
    )

    score = 0

    # Scientific reference documents receive a bonus
    if "scientific_references" in source_name:

        score += 2

    # If the query asks about scientific evidence,
    # strongly prefer reference material.
    if any(
        keyword in query_text
        for keyword in SCIENTIFIC_REFERENCE_KEYWORDS
    ):

        if "scientific_references" in source_name:

            score += 5

    # Match specific FAO concepts
    reference_terms = [
        "recarbonizing global soils",
        "conservation agriculture",
        "soil organic cover",
        "soil biodiversity",
        "water holding capacity"
    ]

    for term in reference_terms:

        if term in query_text and term in chunk_text:

            score += 4

    return score


# ============================================================
# MAIN SEARCH FUNCTION
# ============================================================

def search_knowledge(query, top_k=5):

    if not query:

        return []

    query = str(query).strip()

    if not query:

        return []

    # --------------------------------------------------------
    # Semantic embedding search
    # --------------------------------------------------------

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    )

    # Search more candidates than we finally return.
    # This allows keyword/source reranking.
    candidate_k = min(
        max(top_k * 5, 25),
        len(chunks)
    )

    distances, indices = index.search(
        query_embedding,
        candidate_k
    )

    candidates = []

    # --------------------------------------------------------
    # Build candidate list
    # --------------------------------------------------------

    for rank, idx in enumerate(indices[0]):

        if idx < 0 or idx >= len(chunks):

            continue

        chunk = chunks[idx]

        semantic_distance = float(
            distances[0][rank]
        )

        text = chunk.get(
            "text",
            ""
        )

        semantic_score = 1 / (
            1 + semantic_distance
        )

        kw_score = keyword_score(
            query,
            text
        )

        ref_score = source_bonus(
            query,
            chunk
        )

        # Combined score
        final_score = (
            semantic_score
            + (kw_score * 0.08)
            + (ref_score * 0.10)
        )

        candidates.append(
            {
                "chunk": chunk,
                "semantic_distance": semantic_distance,
                "semantic_score": semantic_score,
                "keyword_score": kw_score,
                "reference_score": ref_score,
                "final_score": final_score
            }
        )

    # --------------------------------------------------------
    # Sort by combined score
    # --------------------------------------------------------

    candidates.sort(
        key=lambda item: item["final_score"],
        reverse=True
    )

    # --------------------------------------------------------
    # Remove duplicate text
    # --------------------------------------------------------

    results = []

    seen_text = set()

    for item in candidates:

        chunk = item["chunk"]

        text = chunk.get(
            "text",
            ""
        ).strip()

        normalized = normalize_text(text)

        if not normalized:

            continue

        if normalized in seen_text:

            continue

        seen_text.add(normalized)

        result = dict(chunk)

        result["score"] = round(
            item["final_score"],
            4
        )

        result["semantic_score"] = round(
            item["semantic_score"],
            4
        )

        result["keyword_score"] = item[
            "keyword_score"
        ]

        result["reference_score"] = item[
            "reference_score"
        ]

        results.append(result)

        if len(results) >= top_k:

            break

    return results


# ============================================================
# COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("======================================")
    print("RAG KNOWLEDGE RETRIEVAL TEST")
    print("======================================")

    query = input(
        "\nEnter your environmental question: "
    )

    results = search_knowledge(
        query,
        top_k=5
    )

    print()
    print(
        f"Retrieved {len(results)} knowledge sources:"
    )

    for i, result in enumerate(
        results,
        start=1
    ):

        print()
        print(
            f"{i}. Source: "
            f"{result.get('source', 'Unknown')}"
        )

        print(
            f"   Score: "
            f"{result.get('score', 0)}"
        )

        print(
            f"   Keyword score: "
            f"{result.get('keyword_score', 0)}"
        )

        print(
            f"   Reference score: "
            f"{result.get('reference_score', 0)}"
        )

        print(
            f"   Text: "
            f"{result.get('text', '')[:500]}"
        )