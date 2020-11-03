import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# TODO: Spotigui.get_songs_from_playlist()

class Spotigui:
    def __init__(self):
        self.scope = "user-read-recently-played user-modify-playback-state"

        with open(os.path.join("código", "config"), "r") as file:
            self.client_id = file.readline().split("=")[1].strip()
            self.client_secret = file.readline().split("=")[1].strip()
            self.redirect_uri = file.readline().split("=")[1].strip()
        
        self.sp = None
        self.playlist = None

        self.auth()
    
    def auth(self):
        if self.client_id is not None and \
            self.client_secret is not None and \
                self.redirect_uri is not None:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=self.scope,
                                                                client_id=self.client_id,
                                                                client_secret=self.client_secret,
                                                                redirect_uri=self.redirect_uri))

    def get_recently_played(self):
        if self.sp is not None:
            result = self.sp.current_user_recently_played()
            ids_recent = list(map(lambda x: x["track"]["id"], result["items"]))
            feats_recent = self.sp.audio_features(ids_recent)
            return feats_recent

    def set_playlist(self, playlist):
        self.playlist = playlist

    def get_songs_from_playlist(self):
        if self.sp is not None and \
            self.playlist is not None:
            pass

