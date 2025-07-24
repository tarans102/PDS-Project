import os
import time

import pandas as pd
import requests
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from dotenv import load_dotenv

from .models import *

dfTMDB = pd.read_csv("MovieRcmdApp/tmdb_5000_movies.csv")


def index(request):
    if "userID" not in request.session:
        request.session["userID"] = 1
    if request.method == "POST":
        request.session["userID"] = int(request.POST["userID"])
    userID = request.session["userID"]
    collabMoviesList = requests.post(
        "http://127.0.0.1:5000/recommendusercollab",
        json={"userID": userID},
    ).json()["1"]
    overviewMoviesList = requests.post(
        "http://127.0.0.1:5000/recommendmovcossimuser",
        json={"userID": userID, "cosSimMatrixID": 1},
    ).json()["1"]
    castMoviesList = requests.post(
        "http://127.0.0.1:5000/recommendmovcossimuser",
        json={"userID": userID, "cosSimMatrixID": 2},
    ).json()["1"]
    keywordsMoviesList = requests.post(
        "http://127.0.0.1:5000/recommendmovcossimuser",
        json={"userID": userID, "cosSimMatrixID": 3},
    ).json()["1"]
    genreMoviesList = requests.post(
        "http://127.0.0.1:5000/recommendmovcossimuser",
        json={"userID": userID, "cosSimMatrixID": 4},
    ).json()["1"]

    allMoviesList = [
        collabMoviesList,
        overviewMoviesList,
        castMoviesList,
        keywordsMoviesList,
        genreMoviesList,
    ]
    for movieList in allMoviesList:
        for movie in movieList:
            moviePosterObj = MoviePosters.objects.get(id=int(movie["id"]))
            movie["backdrop_path"] = moviePosterObj.backdrop_path
            movie["poster_path"] = moviePosterObj.poster_path
            movie["runtime"] = int(movie["runtime"])
    return render(
        request,
        "index.html",
        context={
            "collabMoviesList": collabMoviesList,
            "overviewMoviesList": overviewMoviesList,
            "castMoviesList": castMoviesList,
            "keywordsMoviesList": keywordsMoviesList,
            "genreMoviesList": genreMoviesList,
        },
    )


def moviePage(request, movieID):
    movieRow = dfTMDB.loc[dfTMDB["id"] == movieID]
    movieTitle = movieRow["title"].tolist()[0]
    movieOverview = movieRow["overview"].tolist()[0]
    movieRating = movieRow["vote_average"].tolist()[0] / 2
    movieRuntime = int(movieRow["runtime"].tolist()[0])
    moviePoster = MoviePosters.objects.get(id=movieID).poster_path
    movieBackdrop = MoviePosters.objects.get(id=movieID).backdrop_path
    curMovie = {
        "title": movieTitle,
        "overview": movieOverview,
        "poster_path": moviePoster,
        "backdrop_path": movieBackdrop,
        "rating": movieRating,
        "runtime": movieRuntime,
    }

    overviewMoviesList = requests.post(
        "http://127.0.0.1:5000/recommendmovcossimmov",
        json={"movieID": movieID, "cosSimMatrixID": 1},
    ).json()["1"]
    castMoviesList = requests.post(
        "http://127.0.0.1:5000/recommendmovcossimmov",
        json={"movieID": movieID, "cosSimMatrixID": 2},
    ).json()["1"]
    keywordsMoviesList = requests.post(
        "http://127.0.0.1:5000/recommendmovcossimmov",
        json={"movieID": movieID, "cosSimMatrixID": 3},
    ).json()["1"]
    genreMoviesList = requests.post(
        "http://127.0.0.1:5000/recommendmovcossimmov",
        json={"movieID": movieID, "cosSimMatrixID": 4},
    ).json()["1"]
    allMoviesList = [
        overviewMoviesList,
        castMoviesList,
        keywordsMoviesList,
        genreMoviesList,
    ]
    for movieList in allMoviesList:
        for movie in movieList:
            moviePosterObj = MoviePosters.objects.get(id=int(movie["id"]))
            movie["backdrop_path"] = moviePosterObj.backdrop_path
            movie["poster_path"] = moviePosterObj.poster_path
    return render(
        request,
        "movie.html",
        context={
            "curMovie": curMovie,
            "overviewMoviesList": overviewMoviesList,
            "castMoviesList": castMoviesList,
            "keywordsMoviesList": keywordsMoviesList,
            "genreMoviesList": genreMoviesList,
        },
    )


api_key = os.getenv("TMDB_API_KEY")


def get_movie_poster_path_by_id(movie_id):
    try:
        m = MoviePosters.objects.get(id=movie_id)
    except ObjectDoesNotExist:
        urlMovie = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"

        responseMovie = requests.get(urlMovie)
        print(responseMovie)
        data = responseMovie.json()
        poster_path = None
        backdrop_path = None
        if "poster_path" in data:
            poster_path = data["poster_path"]
        else:
            print(f"Poster not found for {movie_id}")

        if "backdrop_path" in data:
            backdrop_path = data["backdrop_path"]
        else:
            print(f"Backdrop not found for {movie_id}")

        m = MoviePosters.objects.create(
            id=movie_id, poster_path=poster_path, backdrop_path=backdrop_path
        )
        m.save()


def fillDB(request):
    listOfIDs = [i[1]["id"] for i in dfTMDB.iterrows()]
    curID = 1423
    while curID < len(listOfIDs):
        movieID = listOfIDs[curID]
        try:
            m = MoviePosters.objects.get(id=movieID)
            print(movieID)
        except ObjectDoesNotExist:
            get_movie_poster_path_by_id(movieID)
        curID += 1
        time.sleep(1 / 30)

    return HttpResponse("DB FILLED!")
