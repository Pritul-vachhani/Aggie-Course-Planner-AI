import os
import time
from pathlib import Path

import numpy as np

from app.services.catalog import load_catalog
from app.services.recommender import _to_model_data
from Recomend_system import OnnxSentenceEncoder


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main() -> None:
    data = _to_model_data(load_catalog())
    sentences = [
        f"{title}. {description or ''}"
        for title, description in zip(data["title"], data["description"])
    ]
    output_path = Path(os.environ["COURSE_EMBEDDINGS_PATH"])

    start = time.perf_counter()
    embeddings = OnnxSentenceEncoder(MODEL_NAME).encode(sentences)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(output_path, embeddings)
    print(f"Embedded {len(sentences)} courses in {time.perf_counter() - start:.1f} seconds.")


if __name__ == "__main__":
    main()
