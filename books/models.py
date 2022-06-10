from datetime import timedelta

from django.contrib import admin
from django.db import models
from django.db.models import Max, Q, QuerySet
from django.forms import ValidationError
from django.utils.timezone import now as _now_
from django.utils.translation import ugettext_lazy as _
from isbn_field import ISBNField


def _bound_text(text, limit=100):
    return text if len(text) < limit else text[:limit] + '...'


class Publisher(models.Model):
    name = models.CharField(max_length=256, verbose_name=_('Name'))

    class Meta:
        verbose_name = _('Publisher')
        verbose_name_plural = _('Publishers')

    def __str__(self):
        return _bound_text(self.name)

    @staticmethod
    def find_by_name_exact(publisher_name) -> QuerySet:
        return Publisher.objects.filter(name__iexact=publisher_name)


class Shelf(models.Model):
    ddc = models.CharField(blank=True, null=True,
                           max_length=10, verbose_name=_('DDC'))
    description = models.CharField(
        max_length=1024, verbose_name=_('Description'))

    class Meta:
        verbose_name = _('Subject')
        verbose_name_plural = _('Subjects')

    def __str__(self):
        return _bound_text(f"{self.ddc + ' - ' if self.ddc else ''} {self.description}")

    @staticmethod
    def find_equals(other) -> QuerySet:
        return Shelf.objects.filter(ddc=other.ddc, description=other.description)


class Translator(models.Model):
    name = models.CharField(max_length=256, verbose_name=_('Name'))

    class Meta:
        verbose_name = _('Translator')
        verbose_name_plural = _('Translators')

    def __str__(self):
        return self.name

    @staticmethod
    def find_by_name_exact(translator_name) -> QuerySet:
        return Translator.objects.filter(Q(name__iexact=translator_name))


class Collection(models.Model):
    name = models.CharField(max_length=256, verbose_name=_('Name'))
    # publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT, verbose_name=_('Publisher'))

    class Meta:
        verbose_name = _('Collection')
        verbose_name_plural = _('Collections')

    def __str__(self):
        return self.name

    @staticmethod
    def find_by_name_exact(collection_name) -> QuerySet:
        return Collection.objects.filter(name__iexact=collection_name)


class Author(models.Model):
    name = models.CharField(max_length=256, verbose_name=_('Name'))
    year_of_birth = models.CharField(
        max_length=10, blank=True, null=True, verbose_name=_('Year of birth'))
    year_of_death = models.CharField(
        max_length=10, blank=True, null=True, verbose_name=_('Year of death'))
    pha = models.PositiveIntegerField(
        blank=True, null=True, verbose_name=_('PHA'))
    pha_label = models.CharField(
        max_length=10, blank=True, null=True, verbose_name=_('PHA Label'))
    observation = models.TextField(
        blank=True, null=True, verbose_name=_('Observation'))

    class Meta:
        verbose_name = _('Author')
        verbose_name_plural = _('Authors')

    def __str__(self):
        return self.name

    @staticmethod
    def find_equals(other) -> QuerySet:
        return Author.objects.filter(
            Q(name=other.name),
            Q(year_of_birth=other.year_of_birth),
            Q(year_of_death=other.year_of_death),
            Q(pha=other.pha),
            Q(pha_label=other.pha_label),
            Q(observation=other.observation),
        )

    @staticmethod
    def find_by_name_exact(author_name) -> QuerySet:
        return Author.objects.filter(Q(name__iexact=author_name))


class BookStatus(models.TextChoices):
    circulant = 'circulant', _('Circulant')
    archived = 'archived', _('Archived')
    lost_by_user = 'lost_by_user', _('Downed / Lost by user')
    defective = 'defective', _('Downed / Defective book')
    not_circulant = 'not_circulant', _('Not circulant')


class Book(models.Model):
    isbn = ISBNField(blank=True, null=True, verbose_name=_('ISBN'))
    title = models.CharField(max_length=1024, verbose_name=_('Title'))
    authors = models.ManyToManyField(Author, verbose_name=_('Authors'))
    translators = models.ManyToManyField(
        Translator, blank=True, verbose_name=_('Translators'))
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, blank=True, null=True, verbose_name=_('Collection'))
    volume = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_('Volume'))
    edition = models.PositiveIntegerField(
        blank=True, null=True, verbose_name=_('Edition'))
    local = models.CharField(max_length=100, blank=True,
                             null=True, verbose_name=_('Local'))
    publisher = models.ForeignKey(
        Publisher, on_delete=models.PROTECT, blank=True, null=True, verbose_name=_('Publisher'))
    year = models.IntegerField(blank=True, null=True, verbose_name=_('Year'))
    page_count = models.CharField(
        max_length=50, blank=True, null=True, verbose_name=_('Page count'))
    pha = models.CharField(max_length=50, blank=True,
                           null=True, verbose_name=_('PHA'))

    class Meta:
        verbose_name = _('Book')
        verbose_name_plural = _('Books')

    @admin.display(description=_('Title'))
    def title_str(self):

        data = [self.title]

        if self.volume:
            data.append(f"{_('Volume')} {self.volume}")

        if self.edition:
            data.append(f"{_('Edition')} {self.edition}")

        return ' | '.join(data)

    @admin.display(description=_('Authors'))
    def authors_str(self):
        return ' | '.join([str(author) for author in self.authors.all()])

    @admin.display(description=_('Translators'))
    def translators_str(self):
        return ' | '.join([str(translator) for translator in self.translators.all()])

    def infos(self):
        infos = []

        if self.isbn:
            infos.append(f"{_('ISBN')}: {self.isbn}")

        if self.publisher:
            infos.append(f"{_('Publisher')}: {self.publisher}")

        if self.collection:
            infos.append(f"{_('Collection')}: {self.collection}")

        translators_count = self.translators.count()
        if translators_count > 0:
            translator_prefix = _(
                'Translator' if translators_count == 1 else 'Translators')
            infos.append(f"{translator_prefix}: {self.translators_str()}")

        return infos

    def __str__(self):
        return self.title_str()

    @staticmethod
    def search_by_text(search_text) -> QuerySet:
        return Book.objects.filter(
            Q(isbn__iexact=search_text) |
            Q(title__icontains=search_text) |
            Q(authors__name__icontains=search_text) |
            Q(authors__observation__icontains=search_text) |
            Q(collection__name__icontains=search_text)
        ).distinct()

    @staticmethod
    def find_equals(other, authors, translators) -> QuerySet:
        query = Q()
        query.add(Q(title=other.title), Q.AND)
        query.add(Q(collection=other.collection), Q.AND)
        query.add(Q(volume=other.volume), Q.AND)
        query.add(Q(edition=other.edition), Q.AND)
        query.add(Q(local=other.local), Q.AND)
        query.add(Q(publisher=other.publisher), Q.AND)
        query.add(Q(year=other.year), Q.AND)
        query.add(Q(page_count=other.page_countitle_strt), Q.AND)
        query.add(Q(isbn=other.isbn), Q.AND)
        query.add(Q(pha=other.pha), Q.AND)
        query.add(Q(shelf=other.shelf), Q.AND)
        query.add(Q(observations=other.observations), Q.AND)

        if authors:
            query.add(
                Q(authors__name__in=[author.name for author in authors]), Q.AND)

        if translators:
            query.add(Q(translators__name__in=[
                      translator.name for translator in translators]), Q.AND)

        return Book.objects.filter(query)


class PhysicalBook(models.Model):
    physical_id = models.PositiveIntegerField(
        unique=True, verbose_name=_('Physical ID'))
    book = models.ForeignKey(
        Book, on_delete=models.PROTECT, null=False, verbose_name=_('Book'))
    shelf = models.ForeignKey(
        Shelf, on_delete=models.PROTECT, blank=True, null=True, verbose_name=_('Subject'))
    observations = models.TextField(
        max_length=2048, blank=True, null=True, verbose_name=_('Observations'))
    status = models.CharField(max_length=255, choices=BookStatus.choices, verbose_name=_(
        'Status'), default=BookStatus.circulant)

    class Meta:
        verbose_name = _('Physical Book')
        verbose_name_plural = _('Physical Books')

    @admin.display(description=_('Title'))
    def book_title_str(self):
        return self.book.title_str()

    @admin.display(description=_('Authors'))
    def book_authors_str(self):
        return self.book.authors_str()

    @admin.display(description=_('Publisher'))
    def book_publisher_str(self):
        return str(self.book.publisher)

    @admin.display(description=_('Collection'))
    def book_collection_str(self):
        return str(self.book.collection)

    @staticmethod
    def find_equals(other) -> QuerySet:
        return PhysicalBook.objects.filter(
            physical_id=other.dv,
            book=other.book,
            shelf=other.shelf,
            observations=other.observations,
            status=other.status,
        )

    @staticmethod
    def next_physical_id():
        max_id = PhysicalBook.objects.aggregate(Max('physical_id'))[
            'physical_id__max']
        return max_id + 1 if max_id else 1

    def __str__(self):
        return "{physical_id} | {title} | {authors}".format(physical_id=self.physical_id, title=self.book_title_str(), authors=self.book_authors_str())


class Reader(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    document = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Document'))
    contact = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Contact'))
    birthday = models.DateField(
        blank=True, null=True, verbose_name=_('Birthday'))
    observation = models.TextField(blank=True, verbose_name=_('Observation'))

    class Meta:
        verbose_name = _('Reader')
        verbose_name_plural = _('Readers')

    def __str__(self) -> str:
        return '{} | {}'.format(self.id, self.name)


class Borrow(models.Model):
    book = models.ForeignKey(
        PhysicalBook, on_delete=models.PROTECT, verbose_name=_('Book'))
    reader = models.ForeignKey(
        Reader, on_delete=models.PROTECT, verbose_name=_('Reader'))
    date_borrow = models.DateField(
        default=_now_, verbose_name=_('Date borrow'))
    date_return = models.DateField(blank=True, null=True, verbose_name=_(
        'Date return'))
    renew_count = models.PositiveIntegerField(
        verbose_name=_('Renew count'), default=0)
    observation = models.TextField(
        blank=True, null=True, verbose_name=_('Observation'))

    @admin.display(description=_('Status'))
    def status_str(self):
        date_limit = self.date_borrow + timedelta(weeks=1 + self.renew_count)

        if self.date_return:
            if self.date_return > date_limit:
                return _('Returned late')
            return _('Returned')

        if _now_().date() > date_limit:
            return _('Late')
        return _('Borrowed')

    class Meta:
        verbose_name = _('Borrow')
        verbose_name_plural = _('Borrows')

    def clean(self) -> None:
        super().clean()

        errors = {}

        if self.book_id and Borrow.objects.filter(~Q(id=self.id), book=self.book, date_return__isnull=True).exists():
            errors['book'] = _('This book is already borrowed')

        if self.date_return and self.date_return < self.date_borrow:
            errors['date_return'] = _(
                'Return date cannot be before borrow date')

        if errors:
            raise ValidationError(errors)
