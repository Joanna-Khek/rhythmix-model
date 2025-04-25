import pandas as pd
from dotenv import load_dotenv
import os
import time
from pathlib import Path
from typing import List, Literal
from qdrant_client import QdrantClient
from qdrant_client.http import models
from rhythmix_model.configs import settings


def set_up_vectors(data_path: Path) -> pd.DataFrame:
    """Set up vectors for the cleaned dataset.

    Args:
        data_path (Path): Path to the cleaned dataset.

    Returns:
        pd.DataFrame: DataFrame containing the track vectors.
    """
    df = pd.read_csv(data_path)
    df_vectors = df.loc[
        :,
        [
            "track_id",
            "track_link",
            "artists",
            "track_name",
            "track_genre",
            "danceability",
            "energy",
            "key",
            "loudness",
            "mode",
            "speechiness",
            "acousticness",
            "instrumentalness",
            "liveness",
            "valence",
            "tempo",
            "time_signature",
        ],
    ]

    return df_vectors


def batch_upsert(
    client: QdrantClient,
    collection_name: str,
    points: List[models.PointStruct],
    BATCH_SIZE: int = 100,
) -> None:
    """Upsert data to Qdrant in batches.

    Args:
        client (QdrantClient): Qdrant client instance.
        collection_name (str): Name of the collection to upsert data into.
        points (List[models.PointStruct]): List of points to upsert.
        BATCH_SIZE (int, optional): Number of rows to insert to database at one time. Defaults to 100.
    """

    for i in range(0, len(points), BATCH_SIZE):
        batch = points[i : i + BATCH_SIZE]
        try:
            client.upsert(collection_name=collection_name, points=batch)
        except Exception as e:
            print(f"Batch {i//BATCH_SIZE + 1} failed: {e}")
            time.sleep(1)


def create_vector_db(
    client: QdrantClient,
    df_vectors: pd.DataFrame,
    distance_metric: Literal["cosine", "euclidean"],
    collection_name: str,
) -> None:
    """Create the vector database in Qdrant.

    Args:
        client (QdrantClient): Qdrant client instance.
        df_vectors (pd.DataFrame): DataFrame containing the track vectors.
        distance_metric (str): Distance metric to use for the vector database.
        collection_name (str): Name of the collection to create.
    """

    # 1. Determine distance metric
    if distance_metric == "cosine":
        distance = models.Distance.COSINE
    elif distance_metric == "manhattan":
        distance = models.Distance.MANHATTAN
    elif distance_metric == "euclidean":
        distance = models.Distance.EUCLID
    else:
        raise ValueError("Invalid distance metric. Choose 'cosine' or 'manhattan'.")

    # 2. Create collection with a valid name and vector size
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=12, distance=distance),
    )

    # 3. Prepare data for Qdrant
    points = []
    for idx, row in df_vectors.iterrows():
        vector = [
            row["danceability"],
            row["energy"],
            row["key"],
            row["loudness"],
            row["mode"],
            row["speechiness"],
            row["acousticness"],
            row["instrumentalness"],
            row["liveness"],
            row["valence"],
            row["tempo"],
            row["time_signature"],
        ]
        payload = {
            "track_genre": row["track_genre"],
            "track_name": row["track_name"],
            "track_id": row["track_id"],
            "track_artist": row["artists"],
            "track_link": row["track_link"],
        }

        point = models.PointStruct(id=idx, vector=vector, payload=payload)
        points.append(point)

    # 4. Push data to Qdrant
    batch_upsert(client=client, collection_name=collection_name, points=points)


if __name__ == "__main__":
    load_dotenv(settings.ROOT / ".env")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "Missing OPENAI_API_KEY in environment variables. Please set it up in your .env file. "
        )

    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    if not QDRANT_API_KEY:
        raise RuntimeError(
            "Missing QDRANT_API_KEY in environment variables. Please set it up in your .env file."
        )

    QDRANT_ENDPOINT = os.getenv("QDRANT_ENDPOINT")
    if not QDRANT_ENDPOINT:
        raise RuntimeError(
            "Missing QDRANT_ENDPOINT in environment variables. Please set it up in your .env file."
        )

    # Set up the Qdrant client
    client = QdrantClient(url=QDRANT_ENDPOINT, api_key=QDRANT_API_KEY)

    # Prepare the vectors to be inserted into the database
    df_vectors = set_up_vectors(data_path=Path(settings.DATA_DIR, "clean_data.csv"))

    # Create the vector database in Qdrant
    # 1. Cosine distance metric
    create_vector_db(
        client=client,
        df_vectors=df_vectors,
        distance_metric="cosine",
        collection_name="music_vectors",
    )

    # 2. Manhattan distance metric
    create_vector_db(
        client=client,
        df_vectors=df_vectors,
        distance_metric="manhattan",
        collection_name="music_vectors_manhattan",
    )

    # 3. Euclidean distance metric
    create_vector_db(
        client=client,
        df_vectors=df_vectors,
        distance_metric="euclidean",
        collection_name="music_vectors_euclidean",
    )
