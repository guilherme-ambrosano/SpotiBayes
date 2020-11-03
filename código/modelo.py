import pystan
import pandas as pd
from numpy import median, cov
from API import Spotigui

# TODO: próxima música será aquela da playlist que tem
#       médias da posteriori das features mais próxima da média das
#       últimas 10 escutadas hoje que da playlist em si
# TODO: modelo hierárquico de todas as músicas dadas as playlists em que estão

playlist = "música normal só que suave"
sgui = Spotigui()
sgui.set_playlist(playlist)

dados_playlist = pd.DataFrame.from_dict(sgui.get_songs_from_playlist())
dados_playlist = dados_playlist.select_dtypes(exclude=["object"])

dados_playlist = dados_playlist.drop(["key", "mode", "time_signature"], 1)

dados = pd.DataFrame.from_dict(sgui.get_recently_played())
dados = dados.select_dtypes(exclude=["object"])

dados = dados.drop(["key", "mode", "time_signature"], 1)

ultima_musica = dados.iloc[-1]
dados = dados.iloc[0:-1]

# TODO: permitir inserir uma média por feature no modelo
#       para poder colocar constraint em cada uma (<lower=0>)
#       depois colocar tudo num mesmo vetor/matriz (ultima_musica_x)
codigo_stan = """
data {
    int p;
    vector[p] ultima_musica_p;
    vector[p] medias_p;
    matrix[p,p] sigma2_p;
    vector[p] ultima_musica_r;
    vector[p] medias_r;
    matrix[p,p] sigma2_r;
}
parameters {
    vector[p] mu0_p;
    vector<lower=0>[p] sigma02_p;
    vector<lower=0>[p] alfa_p;
    vector<lower=0>[p] beta_p;
    vector[p] mu0_r;
    vector<lower=0>[p] sigma02_r;
    vector<lower=0>[p] alfa_r;
    vector<lower=0>[p] beta_r;
}
model {
    sigma02_p ~ inv_gamma(alfa_p, beta_p);
    mu0_p ~ multi_normal(medias_p, diag_matrix(sigma02_p));
    sigma02_r ~ inv_gamma(alfa_r, beta_r);
    mu0_r ~ multi_normal(medias_r, diag_matrix(sigma02_r));

    ultima_musica_p ~ multi_normal(mu0_p, sigma2_p);
    ultima_musica_r ~ multi_normal(mu0_r, sigma2_r);
}
"""

dados_stan = {"p": len(dados.columns),
              "ultima_musica_p": ultima_musica,
              "medias_p": dados_playlist.mean(),
              "sigma2_p": cov(dados_playlist.transpose()),
              "ultima_musica_r": ultima_musica,
              "medias_r": dados.mean(),
              "sigma2_r": cov(dados.transpose())
              }

try:
    # FIXME: convergência muito ruim e demorando muito tempo pra rodar
    sm = pystan.StanModel(model_code=codigo_stan)
    fit = sm.sampling(data=dados_stan, iter=10000, chains=1)
    print(fit)
except (ValueError, RuntimeError) as e:
    print(e)
