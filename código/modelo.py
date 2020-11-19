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
                       "m": len(df.loc[df.loc[:,var].between(0.01, 0.99)].index),
                       # uns e zeros -> primeira coluna: nem 0 nem 1,
                       #                segunda coluna:  uns
                       #                terceira coluna: zeros
                       "uns_zeros": np.c_[np.array(df.loc[:,var].between(0.01, 0.99)).astype(int),
                           np.array(df.loc[:,var] > 0.99).astype(int),
                           np.array(df.loc[:,var] < 0.01).astype(int)].transpose(),
                       # musicas -> musicas que nao sao 0 nem 1
                       "musicas": df.loc[df.loc[:,var].between(0.01, 0.99), var]
                      }
    else:
        dados_stan = {"n": len(df.index),
                       "musicas": df.loc[:,var]
                      }
    
    sm = carregar_modelo(dist)
    fit = sm.sampling(data=dados_stan, iter=5000, warmup=500, chains=1)
    odict = fit.extract()
    tamanhos = list(map(lambda x: [1 if len(x.shape) == 1 else x.shape[1]][0], odict.values()))
    for i in range(len(odict)):
        if tamanhos[i] > 1:
            chave = list(odict)[i]
            arr = odict.pop(chave)
            for j in range(tamanhos[i]):
                odict.update({str(chave)+str(j): arr[:,j]})
    result = pd.DataFrame(odict, columns=odict.keys()).iloc[:,:-1]
    result_dict = result.to_dict(orient="list")
    return result_dict

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
    for var in VARIAVEIS:
        fits.update({var: rodar_stan(var, VARIAVEIS[var], dados)})
    
    return fits


if __name__ == "__main__":
    sapi = API_spotify()

    # playlist = "tr00"
    playlist = "p/ jogar fifa"
    fits = get_posterioris(sapi, playlist, True)
    print(fits)