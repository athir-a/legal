import argparse
import json
from pathlib import Path

import faiss
import numpy as np
from fastembed import TextEmbedding


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_CORPUS_PATH = PROJECT_ROOT / "data" / "processed" / "legal_chunks.json"
DEFAULT_INDEX_DIR = PROJECT_ROOT / "rag" / "index"
DEFAULT_MODEL_NAME = "BAAI/bge-small-en-v1.5"


def load_corpus(corpus_path: Path):
    with corpus_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Corpus must be a JSON list.")

    for item in data:
        if not item.get("id"):
            raise ValueError("Every chunk must have an id.")
        if not item.get("text"):
            raise ValueError("Every chunk must have text.")

    return data


def build_faiss_index(
    corpus_path=DEFAULT_CORPUS_PATH,
    output_dir=DEFAULT_INDEX_DIR,
    model_name=DEFAULT_MODEL_NAME,
):
    corpus_path = Path(corpus_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading corpus: {corpus_path}")
    corpus = load_corpus(corpus_path)

    texts = [item["text"] for item in corpus]

    print(f"Loading embedding model: {model_name}")
    model = TextEmbedding(model_name=model_name)

    print(f"Embedding {len(texts)} chunks...")
    embeddings = np.array(
        list(model.embed(texts)),
        dtype=np.float32,
    )

    # Normalize for cosine similarity using FAISS inner product
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]

    print(f"Embedding dimension: {dimension}")

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    index_path = output_dir / "legal_index.faiss"
    metadata_path = output_dir / "metadata.json"
    info_path = output_dir / "index_info.json"

    faiss.write_index(index, str(index_path))

    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

    info = {
        "model_name": model_name,
        "dimension": dimension,
        "count": len(corpus),
        "metric": "cosine_similarity",
    }

    with info_path.open("w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)

    print("FAISS index built successfully!")
    print(f"Index: {index_path}")
    print(f"Metadata: {metadata_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--corpus",
        default=str(DEFAULT_CORPUS_PATH),
    )

    parser.add_argument(
        "--output",
        default=str(DEFAULT_INDEX_DIR),
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL_NAME,
    )

    args = parser.parse_args()

    build_faiss_index(
        corpus_path=args.corpus,
        output_dir=args.output,
        model_name=args.model,
    )