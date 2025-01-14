import os
import pandas as pd
from fpgrowth_py import fpgrowth
import re
import pickle
from flask import Flask, request, jsonify
from flask_cors import CORS

MIN_SUPPORT = 0.05
MIN_CONFIDENCE = 0.1

class Recommender:
    def __init__(self, force_create_rules=False):
        # Load dataset and create the name-to-id mapping
        ds1 = pd.read_csv("dataset/2023_spotify_ds1.csv")
        self.train_data = ds1
        self.id_to_name = ds1.set_index("track_uri")["track_name"].to_dict()
        self.name_to_id = ds1.set_index("track_name")["track_uri"].to_dict()

        # Try to load existing rules using pickle
        rules_file_path = self.get_latest_rules_file()
        if rules_file_path and not force_create_rules:
            with open(rules_file_path, "rb") as file:
                self.rules = pickle.load(file)
        else:
            # Run FP-Growth and generate new rules
            grouped_data = ds1.groupby("pid")["track_uri"].apply(list).tolist()
            _, self.rules = fpgrowth(grouped_data, minSupRatio=MIN_SUPPORT, minConf=MIN_CONFIDENCE)
            self.save_rules()

    def get_latest_rules_file(self):
        if not os.path.exists("rules"):
            os.makedirs("rules")
            return None

        rule_files = [f for f in os.listdir("rules") if re.match(r"rule\d+\.pkl", f)]
        if not rule_files:
            return None

        latest_file = max(rule_files, key=lambda x: int(re.findall(r"\d+", x)[0]))
        return os.path.join("rules", latest_file)

    def save_rules(self):
        existing_files = [f for f in os.listdir("rules") if re.match(r"rule\d+\.pkl", f)]
        next_index = max([int(re.findall(r"\d+", f)[0]) for f in existing_files], default=0) + 1
        new_file_path = f"rules/rule{next_index}.pkl"
        with open(new_file_path, "wb") as file:
            pickle.dump(self.rules, file)

    def recommend_songs(self, song_names):
        # Convert song names to URIs
        song_uris = [self.name_to_id.get(song, None) for song in song_names]
        song_uris = [uri for uri in song_uris if uri is not None]

        if not song_uris:
            return []

        recommendations = set()

        # Match each song individually, considering single song rules
        for rule in self.rules:
            antecedent, consequent, confidence = rule
            if any(song in antecedent for song in song_uris):
                recommendations.update(consequent)

        # Convert URIs back to song names
        recommended_songs = [self.id_to_name.get(uri, "Unknown") for uri in recommendations]

        return recommended_songs


app = Flask(__name__)
CORS(app)
app.recommender = Recommender()


@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    songs = data.get("songs", [])
    recommendations = app.recommender.recommend_songs(songs)
    
    # Fetch version from an environment variable
    version = os.getenv("VERSION", "unknown")

    # Fetch the last modified date for the latest rules file
    rules_file_path = app.recommender.get_latest_rules_file()
    model_date = "unknown"
    if rules_file_path:
        model_date = str(pd.to_datetime(os.path.getmtime(rules_file_path), unit='s'))

    return jsonify({
        "songs": recommendations,
        "version": version,
        "model_date": model_date
    })

if __name__ == "__main__":
    app.run()
