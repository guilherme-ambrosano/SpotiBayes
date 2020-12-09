import os
from getpass import getpass

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import pandas as pd
import numpy as np

import scipy
from scipy.stats import beta as Beta
from scipy.stats import gamma
from scipy.stats import norm
import pystan
import pickle

import ast

from flask import Flask, render_template, request, jsonify, abort

PASTA = os.path.dirname(__file__)


def config():
    redirect_uri=input("Redirect URI: ").strip()
    client_id=getpass("Client ID: ").strip()
    client_secret=getpass("Client secret: ").strip()
    return(client_id, client_secret, redirect_uri)


try:
    with open(os.path.join(PASTA, "config.txt"), "r") as config_file:
        CLIENT_ID = config_file.readline().strip("\n").strip()
        CLIENT_SECRET = config_file.readline().strip("\n").strip()
        REDIRECT_URI = config_file.readline().strip("\n").strip()
except:
    CLIENT_ID, CLIENT_SECRET, REDIRECT_URI = config()
    with open(os.path.join(PASTA, "config.txt"), "w") as config_file:
        linhas = [CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]
        config_file.writelines("\n".join(linhas))


class API_spotify:
    def __init__(self):
        self.scope = "user-read-recently-played user-modify-playback-state "\
            "playlist-read-private playlist-read-collaborative playlist-modify-public"
                
        self.sp = None
        self.playlist = None
        self.playlist_id = None

        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.redirect_uri = REDIRECT_URI

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


dist_beta_infl_zero = """
data {
  int<lower=0> n;
  int<lower=0> m;
  int uns_zeros[3,n];
  vector[m] musicas;
}
parameters {  
  simplex[3] theta;
  real<lower=0> alpha;
  real<lower=0> beta;
}
model {
  for (i in 1:n)
    uns_zeros[,i] ~ multinomial(theta);

  musicas ~ beta(alpha, beta);
}
"""

dist_gama = """
data {
  int<lower=0> n;
  vector[n] musicas;
}
parameters {
  real<lower=0> alpha;
  real<lower=0> beta;
}
model {
  musicas ~ gamma(alpha, beta);
}
"""

dist_normal = """
data {
  int<lower=0> n;
  vector[n] musicas;
}
parameters {
  real mu;
  real<lower=0> sigma;
}
model {
  musicas ~ normal(mu, sigma);
}
"""


DISTRIBUICOES = {"beta_infl_zero": dist_beta_infl_zero,
                 "gama": dist_gama,
                 "normal": dist_normal}


VARIAVEIS = {"danceability":     "beta_infl_zero",
             "energy":           "beta_infl_zero",
             "speechiness":      "beta_infl_zero",
             "liveness":         "beta_infl_zero",
             "valence":          "beta_infl_zero",
             "loudness":         "gama",
             "tempo":            "normal",
             "acousticness":     "beta_infl_zero",
             "instrumentalness": "beta_infl_zero"}


def preprocess(df):
    df2 = df.loc[:,VARIAVEIS.keys()]
    df2.loc[:,"loudness"] = -df2.loudness  # invertendo os valores negativos
    return df2


def carregar_modelo(dist):
    try:
        sm = pickle.load(open(os.path.join(PASTA, dist+".pkl"), 'rb'))
        return sm
    except:
        sm = pystan.StanModel(model_code=DISTRIBUICOES[dist], verbose=False)
        with open(os.path.join(PASTA, dist+".pkl"), 'wb') as f:
            pickle.dump(sm, f)
        return sm


def rodar_stan(var, dist, df):
    if dist == "beta_infl_zero":
        uns_zeros = np.c_[np.array(df.loc[:,var].between(0.01, 0.99)).astype(int),
                          np.array(df.loc[:,var] > 0.99).astype(int),
                          np.array(df.loc[:,var] < 0.01).astype(int)]
        dados_stan =  {"n": len(df.index),
                       # m -> numero de musicas que nao sao 0 nem 1
                       "m": len(df.loc[df.loc[:,var].between(0.01, 0.99)].index),
                       # uns e zeros -> primeira coluna: nem 0 nem 1,
                       #                segunda coluna:  uns
                       #                terceira coluna: zeros
                       "uns_zeros": uns_zeros.transpose(),
                       # musicas -> musicas que nao sao 0 nem 1
                       "musicas": df.loc[df.loc[:,var].between(0.01, 0.99), var]
                      }

    else:
        uns_zeros = np.c_[np.ones(len(df.index)), np.zeros(len(df.index)), np.zeros(len(df.index))]
        dados_stan = {"n": len(df.index),
                       "musicas": df.loc[:,var]
                      }
    
    sm = carregar_modelo(dist)
    fit = sm.sampling(data=dados_stan, iter=15000, warmup=5000, seed=9326584,
                      chains=1, control = {"adapt_delta": 0.99})
    odict = fit.extract()
    
    # Pegando só os parametros da playlist
    for par in odict.copy():
        if par.startswith("lp"):
            odict.pop(par)

    # o theta tem 3 colunas - isso vai dar pau depois
    tamanhos = list(map(lambda x: [1 if len(x.shape) == 1 else x.shape[1]][0], odict.values()))
    
    # transformando a array de 3 colunas (theta)
    # em 3 arrays de 1 coluna
    for i in range(len(odict)):
        if tamanhos[i] > 1:
            chave = list(odict)[i]
            arr = odict.pop(chave)
            for j in range(tamanhos[i]):
                odict.update({str(chave)+str(j): arr[:,j]})
    result = pd.DataFrame(odict, columns=odict.keys())
    result_dict = result.to_dict(orient="list")
    
    # verificando se as medias das musicas
    # estão além dos limites de 95% das playlists
    if dist == "beta_infl_zero":
        alpha = fit.summary()["summary"][3,0]
        beta = fit.summary()["summary"][4,0]
        theta0 = fit.summary()["summary"][0,0]
        theta1 = fit.summary()["summary"][1,0]
        theta2 = fit.summary()["summary"][2,0]
        low = Beta.ppf(0.025/theta0, alpha, beta)
        upp = Beta.ppf(1 - 0.025/theta0, alpha, beta)
    elif dist == "gama":
        alpha = fit.summary()["summary"][0,0]
        beta = fit.summary()["summary"][1,0]
        low = gamma.ppf(0.025, alpha, scale=1/beta)
        upp = gamma.ppf(1 - 0.025, alpha, scale=1/beta)
    elif dist == "normal":
        mu = fit.summary()["summary"][0,0]
        sigma = fit.summary()["summary"][1,0]
        low = norm.ppf(0.025, mu, sigma)
        upp = norm.ppf(1 - 0.025, mu, sigma)

    medias = dados_stan["musicas"].to_numpy()
    bools_incompleto = np.logical_and(np.greater_equal(medias, low),
                                      np.less_equal(medias, upp))  # Faltam os uns e zeros

    k = 0
    bools = []
    for j in range(uns_zeros.shape[0]):
        if uns_zeros[j, 0] == 1:
            bools.append(bools_incompleto[k])
            k += 1
        elif uns_zeros[j,1] == 1 and theta1 >= 0.05:
            bools.append(True)
        elif uns_zeros[j,2] == 1 and theta2 >= 0.05:
            bools.append(True)
        else:
            bools.append(False)

    # Calculando as médias
    if dist == "beta_infl_zero":
        theta00 = fit.summary()["summary"][0,0]
        theta01 = fit.summary()["summary"][1,0]
        alfa0 = fit.summary()["summary"][3,0]
        beta0 = fit.summary()["summary"][4,0]

        media = theta00*(alfa0/(alfa0+beta0))+theta01

    elif dist == "gama":
        alfa0 = fit.summary()["summary"][0,0]
        beta0 = fit.summary()["summary"][1,0]
        media = alfa0/beta0

    elif dist == "normal":
        media = fit.summary()["summary"][0,0]
    
    return result_dict, low, media, upp, bools

def get_posterioris(api, playlist=None):
    if playlist is not None:
        api.set_playlist(playlist)
        feats_playlist = pd.DataFrame.from_dict(api.get_songs_from_playlist())
        dados = preprocess(feats_playlist)
    else:
        dados = preprocess(pd.DataFrame.from_dict(api.get_recently_played()))
    
    fits = {}
    lows = {}
    medias = {}
    upps = {}
    bools_dic = {}
    for var in VARIAVEIS:
        result_dict, low, media, upp, bools = rodar_stan(var, VARIAVEIS[var], dados)
        fits.update({var.title(): result_dict})
        lows.update({var: low})
        medias.update({var: media})
        upps.update({var: upp})
        bools_dic.update({var: bools})
    
    if playlist is not None:
        feats_playlist["título"] = feats_playlist.id.map(lambda row: api.sp.track(row)["name"])
        feats_playlist["artista"] = feats_playlist.id.map(lambda row: ", ".join([artista["name"] for artista in api.sp.track(row)["artists"]]))
    else:
        feats_playlist = None
    
    return fits, lows, medias, upps, bools_dic, feats_playlist


if not os.path.isfile(os.path.join(PASTA, ".cache")):
    API_spotify()

sapi = API_spotify()

template_folder = os.path.join(PASTA, 'templates')
static_folder = os.path.join(PASTA, 'static')
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)


@app.route("/")
def home():
    playlists = sapi.get_playlists()
    return render_template("index.html", playlists=playlists)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/get_posterior")
def posterior():
    playlist = request.args.get("playlist")

    fits_file = "fits_" + playlist + ".csv"
    summary_file = "summary_" + playlist + ".csv"
    dentro_file = "dentro_" + playlist + ".csv"

    if os.path.isfile(os.path.join(PASTA, fits_file)) and \
        os.path.isfile(os.path.join(PASTA, summary_file)) and \
            os.path.isfile(os.path.join(PASTA, dentro_file)):

        fits = pd.read_csv(os.path.join(PASTA, fits_file), index_col=0).to_dict()

        for linha in fits:
            for coluna in list(fits[linha].keys()):
                try:
                    fits[linha][coluna] = ast.literal_eval(fits[linha][coluna])
                except ValueError:
                    fits[linha].pop(coluna)


        summary = pd.read_csv(os.path.join(PASTA, summary_file), index_col=0)
        dentro = pd.read_csv(os.path.join(PASTA, dentro_file), index_col=0)

        dentro = dentro.transpose().to_json()
        summary = summary.transpose().to_json()

        result = {"fits": fits,
                  "summary": summary,
                  "dentro": dentro}
        return jsonify(result)
    
    arquivos = os.listdir(PASTA)
    csv = [arquivo for arquivo in arquivos if arquivo.endswith(".csv")]
    for arquivo in csv:
        os.remove(os.path.join(PASTA, arquivo))

    fits, lows, medias, upps, bools_dic, dados = get_posterioris(sapi, playlist)
    dados.loc[:,"loudness"] = -dados.loudness  # invertendo os valores negativos

    bools_df = pd.DataFrame(bools_dic)
    bools_df.columns = [col + '_bool' for col in bools_df.columns]

    dentro = pd.concat([dados, bools_df], axis=1)

    dentro["Total"] = ((dentro.filter(regex="_bool$", axis=1)[dentro==True].sum(axis=1)/
                        dentro.filter(regex="_bool$", axis=1).count(axis=1)))
    dentro["Total"] = (dentro.Total > 2/3)
    
    # Criando a playlist com as músicas selecionadas
    tracks = dentro.loc[dentro.Total==True, "id"]
    if len(tracks) >= 1:
        sapi.create_playlist(tracks)
    
    # Fazendo o summary
    lows = pd.DataFrame(lows, index=["Limite inferior"])
    medias = pd.DataFrame(medias, index=["Media"])
    upps = pd.DataFrame(upps, index=["Limite superior"])
    summary = pd.concat([lows, medias, upps])

    # Pegando só as variáveis importantes
    dentro = dentro.drop(["analysis_url", "id", "key", "mode", "duration_ms", "time_signature",
                          "track_href", "type", "uri"], axis=1)

    # Renomeando as colunas dos dfs
    dentro.columns = map(str.title, dentro.columns)
    summary.columns = map(str.title, summary.columns)

    # Reordenando
    dentro_cols = dentro.columns.tolist()
    summary_cols = summary.columns.tolist()

    dentro_cols = ["Título", "Artista"] + summary_cols + \
        list(map(lambda x: x+"_Bool", summary_cols)) + ["Total"]

    dentro = dentro[dentro_cols]

    pd.DataFrame.from_dict(fits).to_csv(os.path.join(PASTA, fits_file))
    dentro.to_csv(os.path.join(PASTA, dentro_file))
    summary.to_csv(os.path.join(PASTA, summary_file))

    # Transformando em JSON pro site
    dentro = dentro.transpose().to_json()
    summary = summary.transpose().to_json()

    result = {"fits": fits,
              "summary": summary,
              "dentro": dentro}
    return jsonify(result)


if __name__ == "__main__":
    app.run()