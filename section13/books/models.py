from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)


class Book(models.Model):
    title = models.CharField(max_length=20)
    rating = models.IntegerField()
    author = models.ForeignKey(Author, related_name="books", on_delete=models.CASCADE)
