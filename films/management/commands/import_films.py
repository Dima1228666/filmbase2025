from django.core.management.base import BaseCommand
import json
import os
from urllib.request import urlopen
from urllib.error import HTTPError
from django.core.files import File
from tempfile import NamedTemporaryFile
from films.models import Country, Genre, Person, Film, Role, FilmCrew
from .get_films import Command as GetCommand


class Command(BaseCommand):
    help = 'Import films from json file'

    PROFESSION_MAP = {
        'режиссеры': ('director', 'Режиссер'),
        'актеры': ('actor', 'Актер'),
        'продюсеры': ('producer', 'Продюсер'),
        'сценаристы': ('writer', 'Сценарист'),
        'операторы': ('operator', 'Оператор'),
        'композиторы': ('composer', 'Композитор'),
        'художники': ('designer', 'Художник'),
        'монтажеры': ('editor', 'Монтажер'),
        'актеры дубляжа': ('voice-actor', 'Актер дубляжа'),
    }

    def handle(self, *args, **options):
        self.create_films()

    @staticmethod
    def get_image_by_url(url):
        img_tmp = NamedTemporaryFile(delete=True)
        try:
            with urlopen(url) as uo:
                assert uo.status == 200
                img_tmp.write(uo.read())
                img_tmp.flush()
        except HTTPError:
            return None
        return File(img_tmp)

    def create_person(self, data):
        raw_name = data.get('name')
        raw_en_name = data.get('enName')
        final_name = raw_name or raw_en_name or 'Неизвестно'
        print(f"Processing PERSON «{final_name}»")
        attrs = {
            "name": final_name,
            "origin_name": raw_en_name
        }
        try:
            if not data['birthday'].startswith("0000-"):
                attrs['birthday'] = data['birthday'][:10]
        except KeyError:
            pass
        try:
            photo_url = data['photo']
        except KeyError:
            photo_url = None
        person = Person.objects.update_or_create(kinopoisk_id=data['id'],
                                                 defaults=attrs)[0]
        if photo_url:
            image_file = self.get_image_by_url(photo_url)
            if image_file:
                person.photo.save(os.path.basename(photo_url), image_file)
        return person

    def create_film(self, data):
        print(f"Processing FILM «{data['name']}»")
        try:
            cover_url = data['poster']['url']
        except KeyError:
            cover_url = None
        attrs = {"name": data["name"], "origin_name": data["enName"],
                 "slogan": data["slogan"], "length": data["movieLength"],
                 "description": data["description"], "year": data["year"]}
        try:
            attrs["trailer_url"] = data['videos']['trailers'][0]['url']
        except (KeyError, IndexError):
            pass

        film = Film.objects.update_or_create(kinopoisk_id=data['id'],
                                             defaults=attrs)[0]

        if cover_url:
            image_file = self.get_image_by_url(cover_url)
            if image_file:
                film.cover.save(os.path.basename(cover_url), image_file)

        for country_data in data['countries']:
            country_name = country_data['name']
            country = Country.objects.update_or_create(name=country_name)[0]
            film.countries.add(country)

        for genre_data in data['genres']:
            genre_name = genre_data['name']
            genre = Genre.objects.update_or_create(name=genre_name)[0]
            film.genres.add(genre)

        for person_data in data['persons']:
            profession = person_data['profession']
            slug, role_name = self.PROFESSION_MAP[profession]
            role = Role.objects.get_or_create(slug=slug, defaults={'name': role_name})[0]
            person = self.create_person(person_data)
            if person:
                FilmCrew.objects.create(
                    film=film,
                    person=person,
                    role=role
                )

        return film

    def create_films(self):
        with open(GetCommand.filename(), 'r', encoding='utf-8') as f:
            films_data = json.load(f)
            for film_data in films_data['docs']:
                self.create_film(film_data)
