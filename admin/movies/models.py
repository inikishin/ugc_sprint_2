import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('genre_name'), max_length=255)
    description = models.TextField(_('genre_description'), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('genre')
        verbose_name_plural = _('genre_plural')


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('name'), max_length=255)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _('person')
        verbose_name_plural = _('person_plural')


class Filmwork(UUIDMixin, TimeStampedMixin):
    title = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    creation_date = models.DateField(_('creation_date'))
    rating = models.FloatField(_('rating'),
                               blank=True,
                               null=True,
                               validators=[MinValueValidator(0), MaxValueValidator(100)])
    type = models.CharField('type', max_length=255, choices=[('movie', 'Фильм'), ('tv_show', 'ТВ-шоу')])
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')

    def __str__(self):
        return self.title

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('film_work')
        verbose_name_plural = _('film_work_plural')
        indexes = [
            models.Index(fields=['creation_date', 'rating'])
        ]


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    models.UniqueConstraint(fields=['film_work', 'genre'], name='film_work_genre_idx')

    class Meta:
        db_table = "content\".\"genre_film_work"


class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    role = models.TextField(_('role'), max_length=255, null=True)
    created = models.DateTimeField(auto_now_add=True)

    models.UniqueConstraint(fields=['film_work', 'person', 'role'], name='film_work_person_idx')

    class Meta:
        db_table = "content\".\"person_film_work"
