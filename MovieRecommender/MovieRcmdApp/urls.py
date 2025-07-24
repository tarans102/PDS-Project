from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("movie/<int:movieID>", views.moviePage, name="moviePage"),
    # path("f", views.fillDB, name="f"),
]
