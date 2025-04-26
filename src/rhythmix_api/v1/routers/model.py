from typing import Dict
import redis
import uuid
import pickle

from fastapi import APIRouter, HTTPException, status

from rhythmix_api.config import SETTINGS
from rhythmix_model.recommender import graph


ROUTER = APIRouter()
REDIS_CLIENT = redis.Redis(host="localhost", port=6379, db=0)


@ROUTER.post("/predict-attributes", status_code=status.HTTP_200_OK)
async def attributes(prompt: str):
    initial_state = {"user_query": prompt}
    graph_thread = {"configurable": {"thread_id": str(uuid.uuid4())}}

    # Run the graph with initial set up
    graph.compiled_graph.invoke(input=initial_state, config=graph_thread)

    # Get the initial attributes
    graph_state = graph.compiled_graph.get_state(graph_thread)

    # Serialize and store in Redis
    session_id = graph_thread["configurable"]["thread_id"]
    stored_data = {
        "graph_state": pickle.dumps(graph_state),
        "graph_thread": pickle.dumps(graph_thread),
    }
    REDIS_CLIENT.hset(f"session:{session_id}", mapping=stored_data)

    # Optionally set an expiration time (e.g., 1 hour)
    REDIS_CLIENT.expire(f"session:{session_id}", 3600)

    return {"data": graph_state.values, "session_id": session_id}


@ROUTER.post("/song-recommender", status_code=status.HTTP_200_OK)
async def recommender(updated_attributes: Dict, session_id: str) -> Dict:
    """
    Takes in the final adjusted attributes and returns a list of recommended songs.

    Args:
        updated_attributes (Dict): The final adjusted attributes by the user.
        For example,
        updated_attributes =
            {
                "danceability": 0.9
            }

        session_id (str): The redis session ID returned from the /predict-attributes endpoint

    Returns:
        Dict: Keys "similar_songs" and "attributes" where similar songs are the recommended songs and attributes are the final adjusted attributes.
    """
    # Retrieve from Redis
    stored_data = REDIS_CLIENT.hgetall(f"session:{session_id}")
    if not stored_data:
        raise HTTPException(status_code=404, detail="Session not found")

    # Deserialize the graph state and graph thread
    graph_state = pickle.loads(stored_data[b"graph_state"])
    graph_thread = pickle.loads(stored_data[b"graph_thread"])

    # Update the graph state with the new attributes
    graph.compiled_graph.update_state(
        config=graph_state.config,
        values=updated_attributes,
        as_node="predict_attributes",  # according to graph_state's key
    )

    # Get recommendations
    recommendations = graph.compiled_graph.invoke(None, config=graph_thread)

    # Save final results
    results = []
    for songs in recommendations["similar_songs"]:
        results.append(
            {
                "track_name": songs["payload"]["track_name"],
                "track_artist": songs["payload"]["track_artist"],
                "track_genre": songs["payload"]["track_genre"],
                "track_link": songs["payload"]["track_link"],
                "score": songs["score"],
            }
        )

    # Save the final attributes
    attributes = {
        "danceability": recommendations["danceability"],
        "energy": recommendations["energy"],
        "key": recommendations["key"],
        "loudness": recommendations["loudness"],
        "mode": recommendations["mode"],
        "speechiness": recommendations["speechiness"],
        "acousticness": recommendations["acousticness"],
        "instrumentalness": recommendations["instrumentalness"],
        "liveness": recommendations["liveness"],
        "valence": recommendations["valence"],
        "tempo": recommendations["tempo"],
        "time_signature": recommendations["time_signature"],
    }

    # Clean up Redis
    REDIS_CLIENT.delete(f"session:{session_id}")

    return {"similar_songs": results, "attributes": attributes}


@ROUTER.get("/version", status_code=status.HTTP_200_OK)
def model_version() -> Dict:
    return {"version": SETTINGS.VERSION}
