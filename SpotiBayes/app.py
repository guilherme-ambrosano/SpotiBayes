import os
import pandas as pd
from flask import Flask, render_template, request, jsonify, abort

from SpotiBayes.API import API_spotify
from SpotiBayes.modelo import get_posterioris


PASTA = os.path.dirname(__file__)

if not os.path.isfile(os.path.join(PASTA, ".cache")):
    API_spotify()

sapi = API_spotify()

template_folder = os.path.join(PASTA, 'templates')
static_folder = os.path.join(PASTA, 'static')
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)


@app.route("/")
def home():
    playlists = sapi.get_playlists()
    return render_template("index.html", playlists=playlists)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/get_posterior")
def posterior():
    playlist = request.args.get("playlist")
    
    fits, lows, medias, upps, bools_dic, dados = get_posterioris(sapi, playlist)
    dados.loc[:,"loudness"] = -dados.loudness  # invertendo os valores negativos

    bools_df = pd.DataFrame(bools_dic)
    bools_df.columns = [col + '_bool' for col in bools_df.columns]

    dentro = pd.concat([dados, bools_df], axis=1)

    dentro["Total"] = ((dentro.filter(regex="_bool$", axis=1)[dentro==True].sum(axis=1)/
                        dentro.filter(regex="_bool$", axis=1).count(axis=1)))
    dentro["Total"] = (dentro.Total > 2/3)
    
    # Criando a playlist com as músicas selecionadas
    tracks = dentro.loc[dentro.Total==True, "id"]
    if len(tracks) >= 1:
        sapi.create_playlist(tracks)
    
    # Fazendo o summary
    lows = pd.DataFrame(lows, index=["Limite inferior"])
    medias = pd.DataFrame(medias, index=["Média"])
    upps = pd.DataFrame(upps, index=["Limite superior"])
    summary = pd.concat([lows, medias, upps])

    # Pegando só as variáveis importantes
    dentro = dentro.drop(["analysis_url", "id", "key", "mode", "duration_ms", "time_signature",
                          "track_href", "type", "uri"], axis=1)

    # Renomeando as colunas dos dfs
    dentro.columns = map(str.title, dentro.columns)
    summary.columns = map(str.title, summary.columns)

    # Reordenando
    dentro_cols = dentro.columns.tolist()
    summary_cols = summary.columns.tolist()

    dentro_cols = ["Título", "Artista"] + summary_cols + \
        list(map(lambda x: x+"_Bool", summary_cols)) + ["Total"]

    dentro = dentro[dentro_cols]

    pd.DataFrame.from_dict(fits).to_csv(os.path.join(PASTA, "fits.csv"))
    dentro.to_csv(os.path.join(PASTA, "dentro.csv"))
    summary.to_csv(os.path.join(PASTA, "summary.csv"))

    # Transformando em JSON pro site
    dentro = dentro.transpose().to_json()
    summary = summary.transpose().to_json()

    result = {"fits": fits,
              "summary": summary,
              "dentro": dentro}
    return jsonify(result)


if __name__ == "__main__":
    app.run()