import json
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import requests
import youtube_dl
from config.config import config
from exceptions import CustomResponseException

SPOTIFY_TOKEN = config['spotifyToken']
SPOTIFY_USER_ID = config['spotifyUserID']
class PlaylistHandler:

    def __init__(self):
        self.youtube_client = self.get_youtube_client()
        self.all_songs_data = {}

    
    def get_youtube_client(self):
        """Logs into YT, copied from Youtube Web API"""
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secret.json"

        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()

        # from the Youtube DATA API
        youtube_client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        return youtube_client

    def get_liked_videos(self):

        request = self.youtube_client.videos().list(
            part = "snippet,contentDetails,statistics", 
            myRating = "like"
        )
        response = request.execute()

        for item in response["items"]:
            title = item["snippet"]["title"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(item["id"])

            video = youtube_dl.YoutubeDL({}).extract_info(
                youtube_url, download = False)

            song_name = video["track"]
            artist = video["artist"]

            if song_name is not None and artist is not None:

                self.all_songs_data[title]={
                    "youtube_url" : youtube_url, 
                    "song_name" : song_name, 
                    "artist" : artist, 

                    "spotify_uri" : self.get_spotify_uri(song_name, artist)

                }
    
    def create_playlist(self):

        request_body = json.dumps({
            "name" : "Liked Songs from YT", 
            "description": "All Liked Youtube Videos", 
            "public": True
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(
            SPOTIFY_USER_ID)
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(SPOTIFY_TOKEN)
            }
        )
        response_json = response.json()

        # playlist id
        return response_json["id"]


    def get_spotify_uri(self, song_name, artist):

        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(
            song_name,
            artist
        )

        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(SPOTIFY_TOKEN)
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]

        # only use the first song
        uri = songs[0]["uri"]

        return uri

    def add_song_to_playlist(self):
        """Add all liked songs into a new Spotify playlist"""
        # populate dictionary with our liked songs
        self.get_liked_videos()

        # collect all of uri
        uris = [info["spotify_uri"]
                for song, info in self.all_song_info.items()]

        # create a new playlist
        playlist_id = self.create_playlist()

        # add all songs into new playlist
        request_data = json.dumps(uris)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
            playlist_id)

        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(SPOTIFY_TOKEN)
            }
        )

        # check for valid response status
        if response.status_code != 200:
            raise CustomResponseException(response.status_code)

        response_json = response.json()
        return response_json



if __name__ == '__main__':
    handler = PlaylistHandler()
    handler.add_song_to_playlist()