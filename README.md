# SpotiBayes

Este é um projeto realizado para a disciplina LCE5813 - Introdução à Inferência Bayesiana.

O SpotiBayes tem como objetivo utilizar estatística Bayesiana para auxiliar o usuário a organizar suas playlists no Spotify.

# Instalação

1. Baixe e instale o anaconda:

https://www.anaconda.com/products/individual

2. Abra o programa Anaconda Prompt, crie um ambiente e ative-o:

```
conda create -n SpotiBayes python=3.8
conda activate SpotiBayes
```

3. Siga os passos de instalação do pystan:

https://pystan.readthedocs.io/en/latest/windows.html#windows

```
conda install libpython m2w64-toolchain -c msys2
conda install numpy cython matplotlib scipy pandas pystan -c conda-forge
```

4. Instale o spotipy e o Flask:

https://spotipy.readthedocs.io/en/2.16.1/#installation
https://flask.palletsprojects.com/en/1.1.x/installation/

```
pip install spotipy Flask --upgrade
```

5. Talvez seja necessário remover o pacote numpy e scipy instalados pelo conda e reinstalar usando o pip

```
conda remove numpy scipy
pip install numpy==1.19.3 scipy pandas --upgrade
```

6. Instale o SpotiBayes

```
pip install -i https://test.pypi.org/simple/ SpotiBayes-guilherme-ambrosano
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

