import pystan
import pandas as pd
from numpy import median, cov
from API import Spotigui


def preprocess(df):
    df = (df.select_dtypes(exclude=["object"])
            .drop(["key", "mode"], 1))
    return df


# TODO: próxima música será aquela da playlist que tem
#       médias da posteriori das features mais próxima da média das
#       últimas 10 escutadas hoje que da playlist em si

sgui = Spotigui()

playlist = "música normal só que suave"
sgui.set_playlist(playlist)

dados = preprocess(pd.DataFrame.from_dict(sgui.get_songs_from_playlist()))

sgui.set_playlist("Front BR")
dados2 = preprocess(pd.DataFrame.from_dict(sgui.get_songs_from_playlist()))

# TODO: modelo hierárquico de todas as músicas por playlist
#       só precisa atualizar o modelo para as músicas recentes
#       (as playlists não vão mudar)
codigo_stan = """
data {
    int<lower=0> p;
    int<lower=0> n;
    matrix[n,p] musicas;
    vector[p] mu0;
    cov_matrix[p] Sigma;
}
parameters {
    vector[p] mu;
}
model {
    mu ~ multi_normal(mu0, Sigma);
    for (i in 1:n) {
        musicas[i] ~ multi_normal(mu, Sigma);
    }
}
"""

dados_stan = {"p": len(dados.columns),
              "n": len(dados.index),
              "musicas": dados,
              "mu0": dados.mean(),
              "Sigma": cov(dados.transpose()),
             }

dados_stan2 = {"p": len(dados2.columns),
               "n": len(dados2.index),
               "musicas": dados2,
               "mu0": dados2.mean(),
               "Sigma": cov(dados2.transpose()),
              }

sm = pystan.StanModel(model_code=codigo_stan)
fit = sm.sampling(data=dados_stan, iter=5000, warmup=500, chains=1)
fit2 = sm.sampling(data=dados_stan2, iter=5000, warmup=500, chains=1)
print(fit)
print(fit2)
