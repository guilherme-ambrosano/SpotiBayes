import pandas as pd
from flask import Flask, render_template, request, jsonify

from API import API_spotify
from modelo import get_posterioris


app = Flask(__name__)
sapi = API_spotify()

@app.route("/")
def home():
    playlists = sapi.get_playlists()
    return render_template("index.html", playlists=playlists)

@app.route("/get_posterior")
def posterior():
    playlist = request.args.get("playlist")
    print(playlist)
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

    # Pegando só as variáveis importantes e transformando em JSON pro site
    dentro = (dentro
              .drop(["analysis_url", "id", "key", "mode", "duration_ms", "time_signature",
                     "track_href", "type", "uri", ], axis=1)
              .transpose()
              .to_json())
    
    lows = pd.DataFrame(lows, index=[0])
    medias = pd.DataFrame(medias, index=[1])
    upps = pd.DataFrame(upps, index=[2])
    summary = pd.concat([lows, medias, upps]).transpose().to_json()

    result = {"fits": fits,
              "summary": summary,
              "dentro": dentro}
    return jsonify(result)

app.run()