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
    fits, medias, lows, ups, dados = get_posterioris(sapi, playlist)
    dados.loc[:,"loudness"] = -dados.loudness  # invertendo os valores negativos

    dentro = dados.loc[:,:]
    for var in ["danceability", "energy", "loudness", "liveness", "valence", "tempo"]:
        dentro[var+"_bool"] = (dentro[var] >= lows[var]) & (dentro[var] <= ups[var])
    for var in ["speechiness", "acousticness", "instrumentalness"]:
        if medias[var] >= 0.5:
            dentro[var+"_bool"] = dentro[var] >= lows[var]
        else:
            dentro[var+"_bool"] = dentro[var] <= ups[var]

    dentro["Total"] = ((dentro.filter(regex="_bool$", axis=1)[dentro==True].sum(axis=1)/
                        dentro.filter(regex="_bool$", axis=1).count(axis=1)))
    dentro["Total"] = (dentro.Total >= 1/3)
    dentro = (dentro
              .drop(["analysis_url", "id", "key", "mode", "duration_ms", "time_signature",
                     "track_href", "type", "uri", ], axis=1)
              .transpose()
              .to_json())
    
    medias = pd.DataFrame(medias, index=[1])
    lows = pd.DataFrame(lows, index=[0])
    ups = pd.DataFrame(ups, index=[2])

    summary = pd.concat([lows, medias, ups]).transpose().to_json()

    # print(summary)
    # print(dentro)

    result = {"fits": fits,
              "summary": summary,
              "dentro": dentro}
    return jsonify(result)

app.run()