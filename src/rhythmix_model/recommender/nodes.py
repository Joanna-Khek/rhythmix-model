import pandas as pd
import json
import os
from pathlib import Path
from typing import TypedDict
import numpy as np
from qdrant_client.http import models
from qdrant_client import QdrantClient
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from langchain.output_parsers import PydanticOutputParser
from rhythmix_model.recommender.validators import SongAttributes
from rhythmix_model.recommender import prompts
from rhythmix_model.configs import settings
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_ENDPOINT = os.getenv("QDRANT_ENDPOINT")

client = QdrantClient(url=QDRANT_ENDPOINT, api_key=QDRANT_API_KEY)
df = pd.read_csv(Path(settings.DATA_DIR, "clean_data.csv"))
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)


# Initialise the state graph
class State(TypedDict):
    user_query: str
    query_vector: np.array
    llm_response: str
    similar_songs: json
    genre: str
    artists_list: list
    danceability: float
    energy: float
    key: int
    loudness: float
    mode: int
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float
    tempo: float
    time_signature: int


def predict_attributes(state: State):
    """Takes the user_query and send it to the LLM for attributes prediction"""
    parser = PydanticOutputParser(pydantic_object=SongAttributes)
    prompt = PromptTemplate(
        template=prompts.QUERY_PROMPT,
        input_variables=["song_description", "list_of_genres"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | llm | parser
    list_of_genres = list(df.track_genre.unique())

    pred_attributes = chain.invoke(
        {"song_description": state["user_query"], "list_of_genres": list_of_genres}
    )

    return {
        "track_name": pred_attributes.track_name,
        "genre": pred_attributes.genre,
        "artists_list": pred_attributes.artists,
        "danceability": pred_attributes.danceability,
        "energy": pred_attributes.energy,
        "key": pred_attributes.key,
        "loudness": pred_attributes.loudness,
        "mode": pred_attributes.mode,
        "speechiness": pred_attributes.speechiness,
        "acousticness": pred_attributes.acousticness,
        "instrumentalness": pred_attributes.instrumentalness,
        "liveness": pred_attributes.liveness,
        "valence": pred_attributes.valence,
        "tempo": pred_attributes.tempo,
        "time_signature": pred_attributes.time_signature,
    }


def get_similar_songs(state: State):
    """
    1. If track_name is known, filter your Qdrant collection by track_name.
       If no matching record or your Qdrant database doesn't store track_name,
       you can either short-circuit or fallback.
    2. Otherwise, if we have artists_list, filter by artist.
    3. Otherwise, filter by genre.
    4. Run the Qdrant search and return similar_songs.
    """

    track_name = state.get("track_name", None)

    if track_name:
        # Attempt filter by track_name
        filter_condition = models.Filter(
            must=[
                models.FieldCondition(
                    key="track_name", match=models.MatchValue(value=track_name)
                )
            ]
        )
    elif state["artists_list"]:
        filter_condition = models.Filter(
            must=[
                models.FieldCondition(
                    key="track_artist", match=models.MatchAny(any=state["artists_list"])
                )
            ]
        )
    else:
        filter_condition = models.Filter(
            must=[
                models.FieldCondition(
                    key="track_genre", match=models.MatchValue(value=state["genre"])
                )
            ]
        )

    similar_songs_response = client.query_points(
        collection_name="music_vectors",
        query=state["query_vector"],
        limit=5,
        with_payload=True,
        query_filter=filter_condition,
    )

    similar_songs = similar_songs_response.model_dump()["points"]

    # If you want to handle the case where track_name was given,
    # but no Qdrant hits are found (similar_songs is empty),
    # you could fallback to the attribute-based approach here:
    if track_name and not similar_songs:
        # For instance, short-circuit with a single placeholder record
        return {
            "similar_songs": [
                {
                    "payload": {
                        "track_name": track_name,
                        "track_artist": state.get("artists_list", []),
                        "track_genre": state.get("genre", "N/A"),
                        "track_link": "N/A",
                    },
                    "score": 1.0,
                }
            ]
        }

    return {"similar_songs": similar_songs}


def extract_attribute_vectors(state: State):
    """Takes the response from the LLM and extracts the predicted attributes
    into a query vector for the Qdrant API
    """

    query_vector = [
        state["danceability"],
        state["energy"],
        state["key"],
        state["loudness"],
        state["mode"],
        state["speechiness"],
        state["acousticness"],
        state["instrumentalness"],
        state["liveness"],
        state["valence"],
        state["tempo"],
        state["time_signature"],
    ]

    return {"query_vector": query_vector}


def llm_response(state: State):
    parser = StrOutputParser()
    prompt = PromptTemplate(
        template=prompts.RESPONSE_PROMPT,
        input_variables=["model_prediction"],
    )
    chain = prompt | llm | parser
    llm_response = chain.invoke({"model_prediction": state["similar_songs"]})
    return {"llm_response": llm_response}
