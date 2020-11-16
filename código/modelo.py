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


def rodar_stan(var, dist):
    if dist == "beta_infl_zero":
        dados_stan =  {"n": len(dados.index),
                       # m -> numero de musicas que nao sao 0 nem 1
                       "m": len(dados.loc[dados.loc[:,var].between(0.01, 0.99)].index),
                       # uns e zeros -> primeira coluna: nem 0 nem 1,
                       #                segunda coluna:  uns
                       #                terceira coluna: zeros
                       "uns_zeros": np.c_[np.array(dados.loc[:,var].between(0.01, 0.99)).astype(int),
                           np.array(dados.loc[:,var] > 0.99).astype(int),
                           np.array(dados.loc[:,var] < 0.01).astype(int)].transpose(),
                       # musicas -> musicas que nao sao 0 nem 1
                       "musicas": dados.loc[dados.loc[:,var].between(0.01, 0.99), var]
                      }
    else:
        dados_stan = {"n": len(dados.index),
                       "musicas": dados.loc[:,var]
                      }
    
    sm = carregar_modelo(dist)
    fit = sm.sampling(data=dados_stan, iter=5000, warmup=500, chains=1)
    print(fit)

# TODO: próxima música será aquela da playlist que tem
#       médias da posteriori das features mais próxima da média das
#       últimas 10 escutadas hoje que da playlist em si

sapi = API_spotify()

playlist = "tr00"
# playlist = "p/ jogar fifa"

sapi.set_playlist(playlist)

dados = preprocess(pd.DataFrame.from_dict(sapi.get_songs_from_playlist()))

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


# TODO: modelo hierárquico de todas as músicas por playlist
#       só precisa atualizar o modelo para as músicas recentes
#       (as playlists não vão mudar)

for var in VARIAVEIS:
    print(var)
    rodar_stan(var, VARIAVEIS[var])
