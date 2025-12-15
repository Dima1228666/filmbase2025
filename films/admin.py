from django.contrib import admin
from .models import Country, Film, Person, Genre, Role, FilmCrew


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'birthday', 'kinopoisk_id')
    search_fields = ('name',)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class FilmCrewInline(admin.TabularInline):
    model = FilmCrew
    extra = 1
    autocomplete_fields = ['person', 'role']
    ordering = ('role__name',)

@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'length')
    search_fields = ('name',)
    inlines = [FilmCrewInline]
    filter_horizontal = ('genres', 'countries')

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


admin.site.register(Genre)
