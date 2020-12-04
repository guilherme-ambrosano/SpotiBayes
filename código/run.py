import os
from app import app
from API import API_spotify

if not os.path.isfile(".cache"):
    API_spotify()

app.run()
    