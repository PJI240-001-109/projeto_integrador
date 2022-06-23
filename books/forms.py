from datetime import datetime, timedelta
from django import forms
from django.utils.translation import gettext as _

from books.models import Book, Borrow, PhysicalBook


class BookForm(forms.ModelForm):
    isbn = forms.CharField(widget=forms.TextInput(
        attrs={'onchange': "try_fill_book()"}))

    class Media:
        js = ("js/autofill_book.js",)

    class Meta:
        model = Book
        fields = '__all__'


class PhysicalBookForm(forms.ModelForm):
    physical_id = forms.IntegerField(
        label=_('Physical ID'), initial=PhysicalBook.next_physical_id)

    class Meta:
        model = PhysicalBook
        fields = '__all__'


class BorrowForm(forms.ModelForm):
    expected_return = forms.DateField(
        label=_('Expected return'),
        initial=(datetime.today() + timedelta(weeks=1)).date()
    )

    class Meta:
        model = Borrow
        fields = '__all__'
