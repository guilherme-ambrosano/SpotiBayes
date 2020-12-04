import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from setup import setup

class API_spotify:
    def __init__(self):
        self.scope = "user-read-recently-played user-modify-playback-state "\
            "playlist-read-private playlist-read-collaborative playlist-modify-public"
        
        if not os.path.isfile(os.path.join(".", "config")):
            setup()

        with open(os.path.join(".", "config"), "r") as file:
            self.client_id = file.readline().split("=")[1].strip()
            self.client_secret = file.readline().split("=")[1].strip()
            self.redirect_uri = file.readline().split("=")[1].strip()
        
        self.sp = None
        self.playlist = None
        self.playlist_id = None

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
            result = self.sp.current_user_recently_played(limit=10)
            ids_recent = list(map(lambda x: x["track"]["id"], result["items"]))
            feats_recent = self.sp.audio_features(ids_recent)
            return feats_recent

    def get_playlists(self):
        result = self.sp.user_playlists(user=self.sp.me()["id"])
        spotify = self.sp.user_playlists("spotify")
        playlists = result["items"]
        while result["next"]:
            result = self.sp.next(result)
            playlists.extend(result["items"])
        playlists.extend(spotify["items"])
        return playlists
    
    def set_playlist(self, playlist):
        achou = False
        playlists = self.get_playlists()
        for p in playlists:
            if p["name"] == playlist:
                achou = True
                break
        if achou:
            self.playlist = playlist
            self.playlist_id = p["id"]

    def get_songs_from_playlist(self):
        if self.sp is not None and \
            self.playlist is not None:
            result = self.sp.playlist_tracks(playlist_id=self.playlist_id)
            musicas = result["items"]
            ids_playlist = list(map(lambda x: x["track"]["id"], musicas))
            feats_playlist = self.sp.audio_features(ids_playlist)
            while result["next"]:
                result = self.sp.next(result)
                musicas = result["items"]
                ids_playlist = list(map(lambda x: x["track"]["id"], musicas))
                feats_playlist.extend(self.sp.audio_features(ids_playlist))
            return feats_playlist
    
    def create_playlist(self, tracks):
        playlists = self.get_playlists()
        playlists_names = list(map(lambda x: x["name"], playlists))

        # Excluir a playlist antiga se ela existir
        if "SpotiBayes" in playlists_names:
            for p in playlists:
                if p["name"] == "SpotiBayes":
                    playlist_antiga = p
                    break
            self.sp.current_user_unfollow_playlist(playlist_antiga["id"])
        
        # Criando playlist nova
        playlist_nova = self.sp.user_playlist_create(self.sp.me()["id"], "SpotiBayes")
        # Limite de 100 tracks por request
        tracks_faltantes = tracks
        while len(tracks_faltantes) > 100:
            tracks = tracks_faltantes[0:100]
            tracks_faltantes = tracks_faltantes[100:]
            self.sp.user_playlist_add_tracks(self.sp.me()["id"], playlist_nova["id"], tracks)
        self.sp.user_playlist_add_tracks(self.sp.me()["id"], playlist_nova["id"], tracks_faltantes)


