import openai
import time
from typing import Generator


def authenticate_api(api_key: str) -> bool:
    """Authenticate the OpenAI API key.

    Args:
        api_key (str): Open API Key

    Returns:
        bool: True if the API key is valid, False otherwise
    """
    try:
        client = openai.OpenAI(api_key=api_key)
        client.models.list()
        return True
    except openai.AuthenticationError:
        return False
    except Exception:
        return False


def stream_response(response: str) -> Generator[str, None, None]:
    """Yields the response text word by word with a small delay.

    This function splits the input response into words and yields each word
    followed by a space, simulating a streaming effect by introducing a
    slight delay between each word.

    Args:
        response (str): The full response text to stream.

    Yields:
        str: Each word of the response followed by a space.
    """
    for word in response.split():
        yield word + " "
        time.sleep(0.05)
