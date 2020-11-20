import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import pystan
import pickle

from API import API_spotify


VARIAVEIS = {"danceability":     "beta_infl_zero",
             "energy":           "beta_infl_zero",
             "speechiness":      "beta_infl_zero",
             "liveness":         "beta_infl_zero",
             "valence":          "beta_infl_zero",
             "loudness":         "gamma",
             "tempo":            "normal",
             "acousticness":     "beta_infl_zero",
             "instrumentalness": "beta_infl_zero"}


def preprocess(df):
    df2 = df.loc[:,VARIAVEIS.keys()]
    df2.loc[:,"loudness"] = -df2.loudness  # invertendo os valores negativos
    return df2


def carregar_modelo(dist):
    try:
        sm = pickle.load(open(dist+".pkl", 'rb'))
        return sm
    except:
        sm = pystan.StanModel(dist+".stan", verbose=False)
        with open(dist+".pkl", 'wb') as f:
            pickle.dump(sm, f)
        return sm


def rodar_stan(var, dist, df):
    if dist == "beta_infl_zero":
        dados_stan =  {"n": len(df.index),
                       # m -> numero de musicas que nao sao 0 nem 1
                       "m": len(df.loc[df.loc[:,var].between(0.1, 0.9)].index),
                       # uns e zeros -> primeira coluna: nem 0 nem 1,
                       #                segunda coluna:  uns
                       #                terceira coluna: zeros
                       "uns_zeros": np.c_[np.array(df.loc[:,var].between(0.1, 0.9)).astype(int),
                           np.array(df.loc[:,var] > 0.9).astype(int),
                           np.array(df.loc[:,var] < 0.1).astype(int)].transpose(),
                       # musicas -> musicas que nao sao 0 nem 1
                       "musicas": df.loc[df.loc[:,var].between(0.1, 0.9), var]
                      }
    else:
        dados_stan = {"n": len(df.index),
                       "musicas": df.loc[:,var]
                      }
    
    sm = carregar_modelo(dist)
    fit = sm.sampling(data=dados_stan, iter=10000, warmup=5000, chains=1)
    odict = fit.extract()
    tamanhos = list(map(lambda x: [1 if len(x.shape) == 1 else x.shape[1]][0], odict.values()))
    _ = odict.pop("lp__")
    for i in range(len(odict)):
        if tamanhos[i] > 1:
            chave = list(odict)[i]
            arr = odict.pop(chave)
            for j in range(tamanhos[i]):
                odict.update({str(chave)+str(j): arr[:,j]})
    result = pd.DataFrame(odict, columns=odict.keys())
    result_dict = result.to_dict(orient="list")

    if dist == "beta_infl_zero":
        theta00 = fit.summary()["summary"][0,0]
        theta01 = fit.summary()["summary"][1,0]
        alfa0 = fit.summary()["summary"][3,0]
        beta0 = fit.summary()["summary"][4,0]

        media = theta00*(alfa0/(alfa0+beta0))+theta01

        theta00_low = fit.summary()["summary"][0,3]
        theta01_low = fit.summary()["summary"][1,3]
        alfa0_low = fit.summary()["summary"][3,3]
        beta0_low = fit.summary()["summary"][4,7]

        low = theta00_low*(alfa0_low/(alfa0_low+beta0_low)) + theta01_low

        theta00_up = fit.summary()["summary"][0,7]
        theta01_up = fit.summary()["summary"][1,7]
        alfa0_up = fit.summary()["summary"][3,7]
        beta0_up = fit.summary()["summary"][4,3]
        
        up = theta00_up*(alfa0_up/(alfa0_up+beta0_up)) + theta01_up
    elif dist == "gamma":
        alfa0 = fit.summary()["summary"][0,0]
        beta0 = fit.summary()["summary"][1,0]
        media = alfa0/beta0

        alfa0_low = fit.summary()["summary"][0,3]
        beta0_low = fit.summary()["summary"][1,7]
        low = alfa0_low/beta0_low

        alfa0_up = fit.summary()["summary"][0,7]
        beta0_up = fit.summary()["summary"][1,3]
        up = alfa0_up/beta0_up

    elif dist == "normal":
        media = fit.summary()["summary"][0,0]
        low = fit.summary()["summary"][0,3]
        up = fit.summary()["summary"][0,7]

    return result_dict, media, low, up

def get_posterioris(api, playlist=None, boxplot=False):
    if playlist is not None:
        api.set_playlist(playlist)
        dados = preprocess(pd.DataFrame.from_dict(api.get_songs_from_playlist()))
    else:
        dados = preprocess(pd.DataFrame.from_dict(api.get_recently_played()))

    if boxplot:
        # Boxplots
        plt.subplots_adjust(hspace=0.5, wspace=0.4)
        for i in range(len(dados.columns)):
            plt.subplot(3, 3, i+1)
            var = dados.columns[i]
            y = dados.loc[:, var]
            x = np.random.normal(1, 0.04, size=len(y))

            plt.boxplot(y)
            plt.plot(x, y, "r.", alpha=0.1)
            plt.title(var)
        plt.show()
    
    fits = {}
    medias = {}
    lows = {}
    ups = {}
    for var in VARIAVEIS:
        result_dict, media, low, up = rodar_stan(var, VARIAVEIS[var], dados)
        fits.update({var: result_dict})
        medias.update({var: media})
        lows.update({var: low})
        ups.update({var: up})
    
    return fits, medias, lows, ups, dados


if __name__ == "__main__":
    sapi = API_spotify()

    # playlist = "tr00"
    playlist = "p/ jogar fifa"
    fits, _, _, _, _ = get_posterioris(sapi, playlist, True)
    print(fits)