QUERY_PROMPT = """You are a helpful assistant that predicts song attributes.
Given the following description of a song: {song_description}, you are to output the following in
JSON format whose key is the attribute name and value is the attribute value.
["genre", "artists", "danceability", "energy", "key", "loudness", "mode", "speechiness",
"acousticness", "instrumentalness", "liveness", "valence", "tempo", "time_signature"]

First, predict the genre of the song.
The genre of the song should be from this list: {list_of_genres}

Second, if the description contains name of the song artist. output it as a list.

Third, taking into account the genre of the song, given the following definition for each of the attributes,
output the corresponding values for each attribute.

The attributes are:
1. danceability: A float value between 0 to 1. Danceability measures how suitable a track is for dancing, ranging from 0 to 1. Tracks with high danceability scores are more energetic and rhythmic, making them ideal for dancing.
2. energy: A float value between 0 to 1. Energy represents intensity and activity within a song on a scale from 0 to 1. Tracks with high energy tend to be more fast-paced and intense.
3. key: An integer value between 0 and 11. Key refers to different musical keys assigned integers ranging from 0-11. For example: 0 represents the key of C, 1 represents the key of C♯/D♭, and so on.
4. loudness: A float value between -50 to 5. Loudness indicates how loud or quiet an entire song is in decibels (dB). Positive values represent louder songs while negative values suggest quieter ones.
5. mode: An integer value 0 or 1. The tonal mode of the track, represented by an integer value (0 for minor, 1 for major).
6. speechiness: A float value between 0 to 1. Represents the presence of spoken words in a track. For example: rap music would have a high speechiness value.
7. acousticness:  A float value between 0 to 1.
Represents the extent to which a track possesses an acoustic quality. For example: tracks with high acousticness values sound more acoustic (e.g., natural, non-electronic), while tracks with low acousticness values sound more electronic (e.g., synthetic, artificial).
8. instrumentalness: A float value between 0 to 1.
Represents the likelihood of a track being instrumental. For example, tracks with high instrumentalness values are likely to be instrumental tracks.
9. liveness: A float value between 0 to 1.
Represents the presence of an audience during the recording or performance of a track.
10. valence: A float value between 0 to 1. Represents the musical positiveness conveyed by a track. For example, tracks with high valence sound more positive (e.g., happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g., sad, depressed, angry).
11. tempo: A float value representing the tempo of the track in beats per minute (BPM). For example, a tempo of 60 BPM would be a slow, calm tempo, while a tempo of 120 BPM would be a fast, energetic tempo.
12. time_signature: An integer value representing the number of beats within each bar of the track. For example, a time signature of 4 represents four beats per bar.
"""

RESPONSE_PROMPT = """You are an AI assistant that helps format JSON data into clean and readable Markdown documents.

The user will provide you with a JSON array of songs. Each song contains:
- `track_name`
- `track_artist`
- `track_genre`
- `track_link`
- `score`

Your task is to format the songs into a **Markdown list**, and for each song, include a small table showing the details, like this:
No bullet points please.

**Song Title: track_name**

   | Attribute | Value |
   |---|---|
   | **Artist** | track_artist |
   | **Genre** | track_genre |
   | **Search Score** | score |
   | **Spotify Link** | track_link |

Please format the following JSON into this Markdown style:
{model_prediction}

If the JSON is empty, return exactly this string: `No songs found. Please try again.`
Please return only the formatted Markdown, with no additional text
"""
