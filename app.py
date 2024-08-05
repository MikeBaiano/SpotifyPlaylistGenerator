import argparse
import json
import openai
from dotenv import load_dotenv, dotenv_values
import os
import spotipy
import pprint
import datetime

now = datetime.datetime.now()
date_time_str = now.strftime("%d-%m-%Y-%H-%M-%S")

config = dotenv_values('.env')

openai.api_key = config['OPENAI_API_KEY']

parser = argparse.ArgumentParser(description='Generate a playlist of songs based on a prompt')
parser.add_argument('-p', type=str, default='happy songs', help='The prompt for the playlist')
parser.add_argument('-n', type=int, default=8, help='The number of songs in the playlist')

args = parser.parse_args()



def get_playlist(prompt, count=8):
    example_json = """
    [
        {"song": "Someone Like You", "artist": "Adele"},
        {"song": "Skinny Love", "artist": "Bon Iver"},
        {"song": "Hurt", "artist": "Johnny Cash"},
        {"song": "Everybody Hurts", "artist": "R.E.M."},
        {"song": "The Night We Met", "artist": "Lord Huron"}
    ]
    """

    messages = [
        {"role": "system", "content": """You are a helpful playlist generationg assistant.
        You should generate a list of songs and artists according to a text prompt.
        You should return a JSON array, where each elemet follows the format {"song": <song_title>, "artist": <artist_name>}."""},
        {"role": "user", "content": f"Generate a list of 5 songs and artists according to this prompt: super sad songs"},
        {"role": "assistant", "content": example_json},
        {"role": "user", "content": f"Generate a list of {count} songs and artists according to this prompt: {prompt}"},
    ]

    res = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, max_tokens=300)

    playlist = json.loads(res.choices[0].message.content)
    return playlist

playlist = get_playlist(args.p, args.n)
print(playlist)


sp = spotipy.Spotify(
    auth_manager=spotipy.SpotifyOAuth(
        client_id=config['SPOTIFY_CLIENT_ID'],
        client_secret=config['SPOTIFY_CLIENT_SECRET'],
        redirect_uri=config['SPOTIFY_REDIRECT_URI'],
        scope="playlist-modify-private"
    )
)

current_user = sp.current_user()

assert current_user is not None

track_ids = []

for item in playlist:
    artist, song = item["artist"], item["song"]
    query = f"{song} {artist}"
    search_results = sp.search(q=query, type='track', limit=10)
    track_ids.append(search_results["tracks"]["items"][0]["id"])


# search_results = sp.search(q= "Uptown Funk", type='track', limit=10)
# tracks = [search_results["tracks"]["items"][0]["id"]]
#
playlist_name = f"{args.p} {date_time_str}"

created_palylist = sp.user_playlist_create(
    user=current_user["id"],
    public=False,
    name=playlist_name
)

sp.user_playlist_add_tracks(current_user["id"], created_palylist["id"], track_ids)




#get_playlist("love songs", 2)