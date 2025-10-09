from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название книги")
    author = models.CharField(max_length=100, verbose_name="Автор")
    year = models.IntegerField(verbose_name="Год издания")
    pages = models.IntegerField(verbose_name="Количество страниц")
    genre = models.CharField(max_length=50, verbose_name="Жанр", blank=True)
    description = models.TextField(verbose_name="Описание", blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.author}"
    
    def to_dict(self):
        """Преобразует объект книги в словарь для JSON"""
        return {
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'pages': self.pages,
            'genre': self.genre,
            'description': self.description
        }