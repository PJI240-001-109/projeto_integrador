from datetime import timedelta

from django.contrib.admin import SimpleListFilter
from django.db.models import F
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .forms import BookForm, BorrowForm, PhysicalBookForm
from .models import *


class DefaultModelAdmin(admin.ModelAdmin):
    list_per_page = 100
    actions = None


class DefaultListFilter(SimpleListFilter):
    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }


class PublisherAdmin(DefaultModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)


class ShelfAdmin(DefaultModelAdmin):
    search_fields = ('ddc', 'description',)
    ordering = ('ddc',)


class TranslatorAdmin(DefaultModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)


class CollectionAdmin(DefaultModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)


class AuthorAdmin(DefaultModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)


class BookAdmin(DefaultModelAdmin):
    list_display = (
        'title_str',
        'authors_str',
        'publisher',
        'collection',
    )
    list_display_links = ('title_str',)
    search_fields = (
        'title',
        'isbn',
        'pha',
        'authors__name',
        'publisher__name',
        'collection__name',
    )
    autocomplete_fields = ('collection', 'publisher',
                           'authors', 'translators',)


class PhysicalBookAdmin(DefaultModelAdmin):
    list_display = (
        'physical_id',
        'book_title_str',
        'book_authors_str',
        'shelf',
        'book_publisher_str',
        'book_collection_str',
    )
    list_display_links = ('physical_id', 'book_title_str',)
    search_fields = (
        'physical_id',
        'book__title',
        'book__isbn',
        'book__pha',
        'observations',
        'book__authors__name',
        'book__publisher__name',
        'book__collection__name',
    )
    autocomplete_fields = ('book', 'shelf',)
    list_filter = ('status',)
    readonly_fields = ('date_register',)


class ReaderAdmin(DefaultModelAdmin):
    search_fields = ('name', 'document', 'landline_number_1',
                     'landline_number_2', 'cellphone')
    ordering = ('name',)
    readonly_fields = ('date_register',)


class BorrowStatusFilter(DefaultListFilter):
    title = _('Book status')

    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('borrowed', _('Borrowed')),
            ('returned', _('Returned')),
            (None, _('All')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'borrowed':
                return queryset.filter(date_return__isnull=True)

            if self.value() == 'returned':
                return queryset.filter(date_return__isnull=False)

        return queryset


class BorrowLateFilter(DefaultListFilter):
    title = _('Borrow status')

    parameter_name = 'late'

    def lookups(self, request, model_admin):
        return (
            ('late', _('Late')),
            ('on_time', _('On time')),
            (None, _('All')),
        )

    def queryset(self, request, queryset):
        if self.value():
            date_limit = F('date_borrow') + \
                (timedelta(weeks=1) * (F('renew_count') + 1))
            queryset = queryset.annotate(on_date_limit=Coalesce(
                'date_return', timezone.now().date()))

            if self.value() == 'late':
                return queryset.filter(on_date_limit__gt=date_limit)

            if self.value() == 'on_time':
                return queryset.filter(on_date_limit__lte=date_limit)

        return queryset


class BorrowAdmin(DefaultModelAdmin):
    list_display = ('status_str', 'reader', 'book', 'date_borrow',
                    'renew_count', 'date_return')
    autocomplete_fields = ('book', 'reader')
    search_fields = ('book__book__title', 'reader__name',
                     'reader__document', 'reader__landline_number_1', 'reader__landline_number_2', 'reader__cellphone')
    ordering = ('date_borrow',)
    list_filter = (BorrowStatusFilter, BorrowLateFilter)


admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Shelf, ShelfAdmin)
admin.site.register(Translator, TranslatorAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin, form=BookForm)
admin.site.register(PhysicalBook, PhysicalBookAdmin, form=PhysicalBookForm)
admin.site.register(Reader, ReaderAdmin)
admin.site.register(Borrow, BorrowAdmin, form=BorrowForm)
