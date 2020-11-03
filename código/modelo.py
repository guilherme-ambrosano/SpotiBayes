import pystan
import pandas as pd
from numpy import median, cov
from API import Spotigui

# TODO: fazer uma média e uma variância por feature no modelo
#       para poder colocar constraint em cada uma (<lower=0>)
#       depois colocar tudo num vetor/matriz
# TODO: pegar as músicas de uma playlist para construir a
#       outra hipótese
# TODO: próxima música será aquela da playlist que tem
#       médias da posteriori das features mais próxima da média das
#       últimas 10 escutadas hoje que da playlist em si

sgui = Spotigui()
# sgui.set_playlist()
# dados_playlist = pd.DataFrame.from_dict(sgui.get_songs_from_playlist())
dados = pd.DataFrame.from_dict(sgui.get_recently_played())
dados = dados.select_dtypes(exclude=["object"])

dados = dados.drop(["key", "mode"], 1)

ultima_musica = dados.iloc[-1]
dados = dados.iloc[0:-1]

dados_stan = {"medias": dados.mean(),
              "ultima_musica": ultima_musica,
              "sigma2": cov(dados.transpose())}

codigo_stan = """
data {
    vector[11] ultima_musica;
    vector[11] medias;
    matrix[11,11] sigma2;
}
parameters {
    vector[11] mu0;
    real<lower=0> sigma0;
    real<lower=0> alfa;
    real<lower=0> beta;
}
transformed parameters {
    real<lower=0> sigma02;
    sigma02 = sigma0^2;
}
model {
    sigma02 ~ inv_gamma(alfa, beta);
    mu0 ~ multi_normal(medias, diag_matrix(rep_vector(sigma0, 11)));
    ultima_musica ~ multi_normal(mu0, sigma2);
}
"""

sm = pystan.StanModel(model_code=codigo_stan)
fit = sm.sampling(data=dados_stan, iter=1000, chains=1)

print(fit)
