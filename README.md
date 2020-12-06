# SpotiBayes

Este é um projeto realizado para a disciplina LCE5813 - Introdução à Inferência Bayesiana.

O SpotiBayes tem como objetivo utilizar estatística Bayesiana para auxiliar o usuário a organizar suas playlists no Spotify.

# Instalação

1. Siga os passos de instalação do pystan:

https://pystan.readthedocs.io/en/latest/windows.html#windows

```
conda create -n stan_env
conda activate stan_env
conda install libpython m2w64-toolchain -c msys2
conda install numpy cython matplotlib scipy pandas -c conda-forge
```

2. Siga os passos de instalação do spotipy:

https://spotipy.readthedocs.io/en/2.16.1/#installation

```
pip install spotipy --upgrade
```

3. Instale o SpotiBayes

```
pip install -i https://test.pypi.org/simple/ SpotiBayes-guilherme-ambrosano
```

4. Talvez seja necessário remover os pacotes numpy e scipy instalados pelo conda e reinstalar usando o pip

```
conda remove numpy scipy
pip install numpy scipy
```

# Rodando o SpotiBayes

Rode os seguintes comandos no Python:

```
from SpotiBayes.app import app
app.run()
```

Se essa for a primeira vez rodando o SpotiBayes, serão solicitados os dados da sua API.
Para registrar uma API no Spotify, siga os passos em:

https://developer.spotify.com/documentation/general/guides/app-settings/

Depois de preencher os detalhes da API, você deverá colar no terminal o URL para o qual foi redirecionado no seu navegador.

