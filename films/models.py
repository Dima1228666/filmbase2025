from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime


class MyModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Country(MyModel):
    name = models.CharField("Название", max_length=200, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Страна"
        verbose_name_plural = "Страны"

    def __str__(self):
        return self.name


class Genre(MyModel):
    name = models.CharField("Название", max_length=200, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Person(MyModel):
    name = models.CharField("Имя", max_length=400)
    origin_name = models.CharField("Имя в оригинале", max_length=400,
                                   blank=True, null=True)
    birthday = models.DateField("Дата рождения", blank=True, null=True,
                                validators=[
                                    MaxValueValidator(
                                        limit_value=datetime.date.today)
                                ])
    photo = models.ImageField(
        "Фото", upload_to='photos/', blank=True, null=True)
    kinopoisk_id = models.PositiveIntegerField(
        "Kinopoisk ID", blank=True, null=True)

    def age(self):
        if not self.birthday:
            return None
        today = datetime.date.today()
        return today.year - self.birthday.year \
            - ((today.month, today.day) < (self.birthday.month,
                                           self.birthday.day))

    class Meta:
        ordering = ["name"]
        verbose_name = "Персона"
        verbose_name_plural = "Персоны"

    def __str__(self):
        return self.name


class Film(MyModel):
    name = models.CharField("Имя", max_length=1024)
    origin_name = models.CharField(
        "Название (в оригинале)", max_length=1024, blank=True, null=True)
    slogan = models.CharField("Девиз", max_length=2048, blank=True, null=True)
    countries = models.ManyToManyField(Country, related_name="films", verbose_name="страны")
    genres = models.ManyToManyField(Genre, related_name="films", verbose_name="Жанр")
    length = models.PositiveIntegerField(
        "Продолжительность", blank=True, null=True)
    year = models.PositiveIntegerField("Год выпуска", blank=True, null=True,
                                       validators=[MinValueValidator(
                                           limit_value=1885)])
    trailer_url = models.URLField("Трейлер", blank=True, null=True)
    cover = models.ImageField(
        "Постер", upload_to='covers/', blank=True, null=True)
    description = models.TextField("Описание", blank=True, null=True)
    people = models.ManyToManyField(
        Person,
        through='FilmCrew',
        related_name='films'
    )
    kinopoisk_id = models.PositiveIntegerField(
        "Kinopoisk ID", blank=True, null=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"

    def __str__(self):
        return self.name


class Role(MyModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

    def __str__(self):
        return self.name


class FilmCrew(MyModel):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Участник съемочной группы"
        verbose_name_plural = "Съемочная группа"

    def __str__(self):
        return f"{self.person.name} - {self.role.name} ({self.film.name})"
