from django import forms
from dal import autocomplete
from .models import Country, Genre, Film, Person, FilmCrew
from django.forms import inlineformset_factory


class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['name']


class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name']


class FilmForm(forms.ModelForm):
    class Meta:
        model = Film
        fields = ['name', 'origin_name', 'slogan', 'length', 'year',
                  'trailer_url', 'cover', 'description', 'countries', 'genres']
        widgets = {
            'countries': autocomplete.ModelSelect2Multiple(
                url='films:country_autocomplete'),
            'genres': autocomplete.ModelSelect2Multiple(
                url='films:genre_autocomplete')
        }


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', 'origin_name', 'birthday', 'photo']
        widgets = {
            "birthday": forms.DateInput(attrs={'type': 'date'},
                                        format="%Y-%m-%d")
        }

FilmCrewFormSet = inlineformset_factory(
    Film,
    FilmCrew,
    fields=['person', 'role'],
    extra=0,
    can_delete=True,
    widgets={
        'person': autocomplete.ModelSelect2(url='films:person_autocomplete'),
        # Если ролей много, сюда тоже можно добавить автокомплит
    }
)
