from django.db import models


# Create your models here.
class MoviePosters(models.Model):
    id = models.BigIntegerField(
        primary_key=True,
    )
    backdrop_path = models.TextField(null=True)
    poster_path = models.TextField(null=True)
