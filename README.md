# SpotiBayes

Este é um projeto realizado para a disciplina LCE5813 - Introdução à Inferência Bayesiana.

O *SpotiBayes* tem como objetivo utilizar estatística Bayesiana para auxiliar o usuário a organizar suas playlists no Spotify.

Esse *software* estima, usando uma abordagem bayesiana, os parâmetros de uma playlist com base nas estatísticas das músicas contidas nela.
Diferentemente de outros métodos que sugerem novas músicas para incluir, o *SpotiBayes* auxilia o usuário indicando quais músicas devem ser retiradas de uma playlist, por serem muito discrepantes das demais.

# Instalação

Baixe e instale o anaconda:

https://www.anaconda.com/products/individual

Faça download e extraia os arquivos do SpotiBayes.

Abra o programa Anaconda Prompt, navegue até a pasta extraída e rode o comando:

```
setup.bat
```

Durante a instalação, o programa irá pedir que você confirme a criação de um arquivo chamado ```distutils.cfg``` em uma determinada pasta.
Essa pasta será algo como "C:\Usuários\Usuário\.conda\envs\SpotiBayes\lib\distutils\"
Esse arquivo deve conter o seguinte:

```
[build]
compiler=mingw32
```

Caso o arquivo não exista ou não contenha esse texto, adicione-o manualmente.

Depois disso, continue a instalação.

# Rodando o SpotiBayes

Ainda no anaconda Prompt, rode o comando:

```
python run.py
```

Se essa for a primeira vez rodando o SpotiBayes, serão solicitados os dados da sua API.
Para registrar uma API no Spotify, siga os passos em:

https://developer.spotify.com/documentation/general/guides/app-settings/

Depois de preencher os detalhes da API, você deverá colar no terminal o URL para o qual foi redirecionado no seu navegador.

