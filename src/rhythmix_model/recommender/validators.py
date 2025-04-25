from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class SongAttributes(BaseModel):
    track_name: Optional[str] = Field(
        default=None, description="The track name if explicitly provided by the user"
    )
    genre: str = Field(description="The genre of the song")
    artists: List[str] = Field(
        description="The preferred artists of the recommended songs, if any"
    )
    danceability: float = Field(description="The danceability of the song")
    energy: float = Field(description="The energy of the song")
    key: int = Field(description="The key of the song")
    loudness: float = Field(description="The loudness of the song")
    mode: int = Field(description="The mode of the song")
    speechiness: float = Field(description="Speechiness of the song")
    acousticness: float = Field(description="The acousticness of the song")
    instrumentalness: float = Field(description="The instrumentalness of the song")
    liveness: float = Field(description="The liveness of the song")
    valence: float = Field(description="The valence of the song")
    tempo: float = Field(description="The tempo of the song")
    time_signature: int = Field(description="The time signature of the song")

    @field_validator(
        "danceability",
        "energy",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
    )
    @classmethod
    def validate_zero_to_one(cls, value: float, info):
        if not (0 <= value <= 1):
            raise ValueError(f"{info.field_name} should be between 0 and 1")
        return value

    @field_validator("key")
    @classmethod
    def validate_key(cls, value: int):
        if not (0 <= value <= 11):
            raise ValueError("Key should be between 0 and 11")
        return value

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, value: int):
        if value not in {0, 1}:
            raise ValueError("Mode should be 0 or 1")
        return value

    @field_validator("tempo")
    @classmethod
    def validator_tempo(cls, value: float):
        if value < 0:
            raise ValueError("Tempo should be greater than 0")
        return value
