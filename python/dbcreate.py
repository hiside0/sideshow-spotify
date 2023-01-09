import json
import sqlite3

import spotipy

client_id = ""  # https://developer.spotify.com/dashboard/ から create an appで作成
client_secret = ""  # 上で発行されるものを使用

playlist_id = ""  # プレイリストID
pl_user = ""  # プレイリストオーナーのユーザ名


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


db_path = "data.db"
con = sqlite3.connect(db_path)
cur = con.cursor()
cur.execute(
    "CREATE TABLE IF NOT EXISTS tracks ("
    "id TEXT not null primary key,"
    "name TEXT not null,"
    "popularity INT not null,"
    "uri TEXT not null,"
    "image TEXT not null)"
)

cur.execute(
    "CREATE TABLE IF NOT EXISTS features ("
    "id TEXT not null primary key,"
    "acousticness REAL not null,"
    "danceability REAL not null,"
    "duration_ms INT not null,"
    "energy REAL not null,"
    "instrumentalness REAL not null,"
    "key REAL not null,"
    "liveness REAL not null,"
    "loudness REAL not null,"
    "mode INT not null,"
    "speechiness REAL not null,"
    "tempo REAL not null,"
    "time_signature INT not null,"
    "valence REAL not null)"
)

cur.execute("SELECT id from features;")
exist_features_ids = [one[0] for one in cur.fetchall()]  # 整形

client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(
    client_id, client_secret
)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

res = spotify.user_playlist_tracks(pl_user, playlist_id)
tracks = res["items"]
while res["next"]:
    res = spotify.next(res)
    tracks.extend(res["items"])

for track in tracks:
    sql = (
        "INSERT OR IGNORE INTO tracks ("
        "id, name, popularity, uri, image) "
        'VALUES("{}","{}",{},"{}","{}")'
    ).format(
        track["track"]["id"],
        track["track"]["name"],
        track["track"]["popularity"],
        track["track"]["uri"],
        track["track"]["album"]["images"][0]["url"],
    )
    cur.execute(sql)

    # featuresテーブルにすでにidが存在しない場合のみapiを叩く
    if track["track"]["id"] not in exist_features_ids:
        res = spotify.audio_features(track["track"]["uri"])
        queue = (
            "INSERT OR IGNORE INTO features ("
            "id, acousticness, danceability, duration_ms, energy, "
            "instrumentalness, key, liveness, loudness, mode, "
            "speechiness, tempo, time_signature, valence) "
            'VALUES("{}",{},{},{},{},{},{},{},{},{},{},{},{},{})'
        ).format(
            track["track"]["id"],
            res[0]["acousticness"],
            res[0]["danceability"],
            res[0]["duration_ms"],
            res[0]["energy"],
            res[0]["instrumentalness"],
            res[0]["key"],
            res[0]["liveness"],
            res[0]["loudness"],
            res[0]["mode"],
            res[0]["speechiness"],
            res[0]["tempo"],
            res[0]["time_signature"],
            res[0]["valence"],
        )
        cur.execute(queue)

sql = (
    "CREATE VIEW IF NOT EXISTS features_with_name AS "
    "SELECT DISTINCT "
    "   f.id AS id,"
    "   t.name AS name,"
    "   t.popularity AS popularity,"
    "   t.image AS image,"
    "   f.acousticness AS acousticness,"
    "   f.danceability AS danceability,"
    "   f.duration_ms AS duration_ms,"
    "   f.energy AS energy,"
    "   f.instrumentalness AS instrumentalness,"
    "   f.key AS key,"
    "   f.liveness AS liveness,"
    "   f.loudness AS loudness,"
    "   f.mode AS mode,"
    "   f.speechiness AS speechiness,"
    "   f.tempo AS tempo,"
    "   f.time_signature AS time_signature,"
    "   f.valence AS valence "
    "FROM features f "
    "LEFT JOIN tracks t ON f.id = t.id;"
)
cur.execute(sql)
con.commit()

json_file = open("data.json", "w", encoding="UTF-8", errors="ignore")

con.row_factory = dict_factory
cur = con.cursor()
cur.execute("SELECT * from features_with_name;")
data = cur.fetchall()
json.dump(data, json_file, ensure_ascii=False, indent=4)

con.close()
