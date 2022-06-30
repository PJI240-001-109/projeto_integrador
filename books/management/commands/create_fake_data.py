import json
import urllib.request
from datetime import date, datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Max
from faker import Faker
from faker.providers import date_time, isbn, phone_number, profile

from books.models import Author, Book, Borrow, PhysicalBook, Reader


def build_book(isbn) -> Book:
    base_api_link = 'https://www.googleapis.com/books/v1/volumes?q=isbn:'

    with urllib.request.urlopen(base_api_link + isbn) as f:
        text = f.read()

    api_results = json.loads(text.decode('utf-8'))
    if api_results['totalItems'] == 0:
        return None

    volume_info = api_results['items'][0]['volumeInfo']

    authors = []
    if 'authors' in volume_info:
        for author in volume_info['authors']:
            authors.append(Author.objects.filter(name=author).get_or_create())

    book = Book(
        isbn=isbn,
        title=volume_info['title'],
        year=volume_info['publishedDate'].split('-')[0] if 'publishedDate' in volume_info else None,
        page_count=volume_info['pageCount'] if 'pageCount' in volume_info else None,
    )
    book.save()
    [book.authors.add(author.id) for author in authors if 'id' in author]
    book.save()

    return book


class Command(BaseCommand):
    help = 'Create fake data with Faker'
    base_dir = Path(settings.BASE_DIR, 'books/management/commands')

    def handle(self, *args, **options):
        fake = Faker('pt_BR')
        fake.add_provider(profile)
        fake.add_provider(isbn)
        fake.add_provider(phone_number)
        fake.add_provider(date_time)

        # Readers
        for _ in range(100):
            p = fake.profile()

            Reader(
                name=p['name'],
                document=p['ssn'],
                landline_number_1=fake.phone_number(),
                landline_number_2=fake.phone_number(),
                cellphone=fake.phone_number(),
                email=p['mail'],
                birthday=p['birthdate'],
            ).save()

        # Books
        for i in range(10):
            book = build_book(fake.isbn13() if i % 2 == 0 else fake.isbn10())
            if not book:
                continue

            book.save()

            for _ in range(5):
                physical_id = PhysicalBook.objects.aggregate(max=Max('physical_id'))['max']

                PhysicalBook(
                    physical_id=physical_id + 1 if physical_id else 1,
                    book=book
                ).save()

        # Borrows
        for _ in range(100):
            reader = Reader.objects.order_by('?').first()
            book = PhysicalBook.objects.order_by('?').first()

            first_date = fake.past_date()
            second_date = fake.past_date()

            Borrow(
                book=book,
                reader=reader,
                date_borrow=first_date if first_date <= second_date else second_date,
                date_return=second_date if second_date > first_date else first_date,
                renew_count=0,
                observation=fake.text(),
            ).save()
