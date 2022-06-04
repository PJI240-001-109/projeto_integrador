from .forms import BookForm, PhysicalBookForm
from .models import *

from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter


class DefaultModelAdmin(admin.ModelAdmin):
    list_per_page = 100


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


class ReaderAdmin(DefaultModelAdmin):
    search_fields = ('name', 'document', 'contact')
    ordering = ('name',)


class BorrowStatusFilter(SimpleListFilter):
    title = _('Status')

    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('late', _('Late')),
            ('borrowed', _('Borrowed')),
            ('returned', _('Returned')),
            ('returned_late', _('Returned Late')),
            (None, _('All')),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())

        return queryset


class BorrowAdmin(DefaultModelAdmin):
    autocomplete_fields = ('books', 'reader')
    search_fields = ('books__title', 'reader__name', 'reader__document',)
    ordering = ('date_borrow',)
    list_filter = (BorrowStatusFilter,)


admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Shelf, ShelfAdmin)
admin.site.register(Translator, TranslatorAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin, form=BookForm)
admin.site.register(PhysicalBook, PhysicalBookAdmin, form=PhysicalBookForm)
admin.site.register(Reader, ReaderAdmin)
admin.site.register(Borrow, BorrowAdmin)
