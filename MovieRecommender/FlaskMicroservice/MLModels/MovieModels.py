import joblib
import pandas as pd
from flask import Flask, jsonify, request

app = Flask(__name__)

dfTMDB = pd.read_csv("tmdb_5000_movies.csv")
movieListIndexes = pd.Series(dfTMDB.index, index=dfTMDB["id"]).drop_duplicates()

overviewCosSim = joblib.load("overviewCosSim.joblib")
castCosSim = joblib.load("castCosSim.joblib")
genreCosSim = joblib.load("genreCosSim.joblib")
keywordsCosSim = joblib.load("keywordsCosSim.joblib")
trainset = joblib.load("trainset.joblib")
svd = joblib.load("svd.joblib")

simMatrixDict = {1: overviewCosSim, 2: castCosSim, 3: genreCosSim, 4: keywordsCosSim}


@app.route("/recommendusercollab", methods=["POST"])
def getListUserCollab():
    data = request.json
    userID = data.get("userID")
    movieIndices = recommenderUserCollab(userID, trainset, svd)
    movieList = []
    for i in movieIndices:
        movieDict = {
            "id": str(dfTMDB["id"][i]),
            "title": dfTMDB["title"][i],
            "rating": round(dfTMDB["vote_average"][i] / 2, 1),
            "runtime": dfTMDB["runtime"][i],
        }
        movieList.append(movieDict)
    dict = {"1": movieList}
    return jsonify(dict)


@app.route("/recommendmovcossimuser", methods=["POST"])
def getListCosSimUser():
    data = request.json
    userID = data.get("userID")
    cosSimMatrixID = data.get("cosSimMatrixID")
    cosSimMatrix = simMatrixDict[cosSimMatrixID]
    indices = recommenderGetAll(userID, cosSimMatrix, trainset)
    movieList = []
    for i in indices:
        movieDict = {
            "id": str(dfTMDB["id"][i]),
            "title": dfTMDB["title"][i],
            "rating": round(dfTMDB["vote_average"][i] / 2, 1),
            "runtime": dfTMDB["runtime"][i],
        }
        movieList.append(movieDict)
    dict = {"1": movieList}
    return jsonify(dict)


@app.route("/recommendmovcossimmov", methods=["POST"])
def getListCosSimMov():
    data = request.json
    movieID = data.get("movieID")
    cosSimMatrixID = data.get("cosSimMatrixID")
    cosSimMatrix = simMatrixDict[cosSimMatrixID]
    indices = recommenderCosSimID(movieID, cosSimMatrix)
    movieList = []
    for i in indices:
        movieDict = {
            "id": str(dfTMDB["id"][i]),
            "title": dfTMDB["title"][i],
            "rating": round(dfTMDB["vote_average"][i] / 2, 1),
            "runtime": dfTMDB["runtime"][i],
        }
        movieList.append(movieDict)
    dict = {"1": movieList}
    return jsonify(dict)


def getUserRatedMovies(trainset, rawUserID):
    userInnerId = trainset.to_inner_uid(rawUserID)
    ratedMovies = [
        (trainset.to_raw_uid(itemId), rating)
        for (itemId, rating) in trainset.ur[userInnerId]
    ]
    return ratedMovies


def recommenderGetAll(userID, cosSimMatrix, trainset):
    movieIDs = getUserRatedMovies(trainset, userID)
    movieIDs = sorted(movieIDs, key=lambda x: x[1], reverse=True)
    recommendations = []
    for movie in movieIDs[:5]:
        recommendations.extend(recommenderCosSimIdx(movie[0], cosSimMatrix))
    return recommendations


def recommenderCosSimIdx(movieIdx, cosSimMatrix):
    movies = list(enumerate(cosSimMatrix[movieIdx]))
    recommendations = sorted(movies, key=lambda x: x[1], reverse=True)[1:11]
    movieIndices = [i[0] for i in recommendations]
    return movieIndices


def recommenderCosSimID(movieID, cosSimMatrix):
    movieIndex = movieListIndexes[movieID]
    movies = list(enumerate(cosSimMatrix[movieIndex]))
    recommendations = sorted(movies, key=lambda x: x[1], reverse=True)[1:11]
    movieIndices = [i[0] for i in recommendations]
    return movieIndices


def recommenderUserCollab(userID, trainset, svd):
    def getUnseenItems(trainset, userID):
        seenItems = set([j for (j, _) in trainset.ur[userID]])
        allItems = set(trainset.all_items())
        unseenItems = allItems - seenItems
        return unseenItems

    unseenItems = getUnseenItems(trainset, trainset.to_inner_uid(userID))
    predictions = [
        (
            itemID,
            svd.predict(userID, trainset.to_raw_iid(itemID)).est,
        )
        for itemID in unseenItems
    ]
    topN = sorted(predictions, key=lambda x: x[1], reverse=True)[:20]
    moviesList = [i[0] for i in topN]
    return moviesList


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
