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

    dentro = dados.loc[:,:]
    for var in dentro.columns:
        dentro[var] = (dentro[var] >= lows[var]) & (dentro[var] <= ups[var])
    print((dentro[dentro==True].sum(axis=1)/dentro.count(axis=1)).value_counts())
    return jsonify(fits)

app.run()