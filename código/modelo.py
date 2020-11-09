import pystan
import pandas as pd
from numpy import median, cov
from API import API_spotify
import matplotlib.pyplot as plt


def preprocess(df):
    df2 = df[["danceability", "energy", "speechiness", # beta
              "liveness", "valence",                   # beta
              "loudness",                              # gama
              "tempo"# ,                                 # normal
              # "acousticness", "instrumentalness"     # beta infl zero
              ]]
    df2.loc[:,"loudness"] = -df2.loudness  # invertendo os valores negativos
    return df2


# TODO: próxima música será aquela da playlist que tem
#       médias da posteriori das features mais próxima da média das
#       últimas 10 escutadas hoje que da playlist em si

sapi = API_spotify()

playlist = "cordas dedilhadas"  # FIXME: o modelo só funciona pra algumas playlists
sapi.set_playlist(playlist)

dados = preprocess(pd.DataFrame.from_dict(sapi.get_songs_from_playlist()))

# FIXME: mudar todas as betas pra betas inflacionadas de zero...
#        será que conserta?
# TODO: modelo hierárquico de todas as músicas por playlist
#       só precisa atualizar o modelo para as músicas recentes
#       (as playlists não vão mudar)
codigo_stan = """
data {
    int<lower=0> p;
    int<lower=0> n;
    matrix[n,p] musicas;
}
parameters {
    vector<lower=0>[5] alpha0;
    vector<lower=0>[5] beta0;
    real mu0;
    real<lower=0> sigma0;
    real<lower=0> alpha0_gamma;
    real<lower=0> beta0_gamma;
    vector<lower=0, upper=1>[2] theta0_zinflbeta;
    vector<lower=0>[2] alpha0_zinflbeta;
    vector<lower=0>[2] beta0_zinflbeta;
}
model {
    for (i in 1:n)
        for (j in 1:p)
            if (j <= 5)
                musicas[i, j] ~ beta(alpha0[j], beta0[j]); // transformar todas as betas
                                                           // em beta inflacionada de zero
            else if (j == 6)
                musicas[i, j] ~ gamma(alpha0_gamma, beta0_gamma);
            else if (j == 7)
                musicas[i, j] ~ normal(mu0, sigma0);
            else
                if (musicas[i,j] < 0.01)
                    1 ~ bernoulli(theta0_zinflbeta[j-7]);
                else {
                    0 ~ bernoulli(theta0_zinflbeta[j-7]);
                    musicas[i,j] ~ beta(alpha0_zinflbeta[j-7], beta0_zinflbeta[j-7]);
                }
}
"""

dados_stan = {"p": len(dados.columns),
              "n": len(dados.index),
              "musicas": dados
             }

sm = pystan.StanModel(model_code=codigo_stan)
fit = sm.sampling(data=dados_stan, iter=5000, warmup=500, chains=1)
print(fit)

# sapi.set_playlist("Front BR")
# dados2 = preprocess(pd.DataFrame.from_dict(sapi.get_songs_from_playlist()))
# dados_stan2 = {"p": len(dados2.columns),
#                "n": len(dados2.index),
#                "musicas": dados2
#               }
# fit2 = sm.sampling(data=dados_stan2, iter=5000, warmup=500, chains=1)
# print(fit2)
