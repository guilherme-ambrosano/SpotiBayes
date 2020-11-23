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
        uns_zeros = np.c_[np.array(df.loc[:,var].between(0.1, 0.9)).astype(int),
                          np.array(df.loc[:,var] > 0.9).astype(int),
                          np.array(df.loc[:,var] < 0.1).astype(int)]
        dados_stan =  {"n": len(df.index),
                       # m -> numero de musicas que nao sao 0 nem 1
                       "m": len(df.loc[df.loc[:,var].between(0.1, 0.9)].index),
                       # uns e zeros -> primeira coluna: nem 0 nem 1,
                       #                segunda coluna:  uns
                       #                terceira coluna: zeros
                       "uns_zeros": uns_zeros.transpose(),
                       # musicas -> musicas que nao sao 0 nem 1
                       "musicas": df.loc[df.loc[:,var].between(0.1, 0.9), var]
                      }

    else:
        uns_zeros = np.c_[np.ones(len(df.index)), np.zeros(len(df.index)), np.zeros(len(df.index))]
        dados_stan = {"n": len(df.index),
                       "musicas": df.loc[:,var]
                      }
    
    sm = carregar_modelo(dist)
    #fit = sm.sampling(data=dados_stan, iter=15000, warmup=5000, chains=1)
    fit = sm.sampling(data=dados_stan, iter=1500, warmup=500, chains=1)
    odict = fit.extract()
    
    # Pegando só os parametros das musicas
    odict_musica = odict.copy()
    for par in odict_musica.copy():
        if not par.startswith("musica_"):
            odict_musica.pop(par)

    # Pegando só os parametros da playlist
    for par in odict.copy():
        if not par.startswith("playlist_"):
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
    
    bools = []
    # verificando se as medias das musicas
    # estão além dos limites de 95% das playlists
    for i in range(len(odict_musica)):
        parametro_musica = list(odict_musica.keys())[i]
        parametro_playlist = parametro_musica.replace("musica", "playlist")
        medias = np.mean(odict_musica[parametro_musica], axis=0)
        media = np.mean(odict[parametro_playlist])
        low = np.quantile(odict[parametro_playlist], 0.025)
        up = np.quantile(odict[parametro_playlist], 0.975)
        bools_incompleto = np.logical_and(np.greater_equal(medias, low),
                                          np.less_equal(medias, up))  # Faltam os uns e zeros

        k = 0
        bools_completo = []
        for j in range(uns_zeros.shape[0]):
            if uns_zeros[j, 0] == 1:
                bools_completo.append(bools_incompleto[k])
                k += 1
            elif parametro_musica.endswith("speechiness") and uns_zeros[j, 1] == 1 and media > 2/3:
                bools_completo.append(True)
            elif parametro_musica.endswith("speechiness") and uns_zeros[j, 2] == 1 and media < 1/3:
                bools_completo.append(True)
            elif uns_zeros[j, 1] == 1 and media > 0.5:
                bools_completo.append(True)
            elif uns_zeros[j, 2] == 1 and media < 0.5:
                bools_completo.append(True)
            else:
                bools_completo.append(False)
        bools.append(bools_completo)
        
    bools = tuple(bools)
    bools = np.logical_and.reduce(bools)  # Todos os parâmetros da variável
                                          # precisam estar de acordo com a playlist

    # Calculando as médias
    if dist == "beta_infl_zero":
        theta00 = fit.summary()["summary"][0,0]
        theta01 = fit.summary()["summary"][1,0]
        alfa0 = fit.summary()["summary"][3,0]
        beta0 = fit.summary()["summary"][4,0]

        media = theta00*(alfa0/(alfa0+beta0))+theta01

    elif dist == "gamma":
        alfa0 = fit.summary()["summary"][0,0]
        beta0 = fit.summary()["summary"][1,0]
        media = alfa0/beta0

    elif dist == "normal":
        media = fit.summary()["summary"][0,0]
    
    return result_dict, media, bools

def get_posterioris(api, playlist=None, boxplot=False):
    if playlist is not None:
        api.set_playlist(playlist)
        feats_playlist = pd.DataFrame.from_dict(api.get_songs_from_playlist())
        dados = preprocess(feats_playlist)
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
    bools_dic = {}
    for var in VARIAVEIS:
        result_dict, media, bools = rodar_stan(var, VARIAVEIS[var], dados)
        fits.update({var: result_dict})
        medias.update({var: media})
        bools_dic.update({var: bools})
    
    if playlist is not None:
        feats_playlist["titulo"] = feats_playlist.id.map(lambda row: api.sp.track(row)["name"])
        feats_playlist["artista"] = feats_playlist.id.map(lambda row: ", ".join([artista["name"] for artista in api.sp.track(row)["artists"]]))
    else:
        feats_playlist = None
    
    return fits, medias, bools_dic, feats_playlist


if __name__ == "__main__":
    sapi = API_spotify()

    playlist = "teste"
    fits, _, bools_dic, dados = get_posterioris(sapi, playlist, False)
    bools_df = pd.DataFrame.from_dict(bools_dic)
    bools_df.columns = [col + '_bool' for col in bools_df.columns]

    dentro = pd.concat([dados, bools_df], axis=1)