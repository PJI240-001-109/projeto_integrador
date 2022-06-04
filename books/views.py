from django.core.exceptions import BadRequest
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Author, Book, Publisher
from .serializers import AuthorSerializer, PublisherSerializer


def index(request):
    if 'search' in request.GET and request.GET['search']:
        search_text = request.GET['search']

        if len(search_text) < 3:
            raise BadRequest("Search query must have at least 3 characters")

        result = Book.search_by_text(search_text)

        return render(request, 'index.html', {'books': result, 'search_text': search_text})

    return render(request, 'index.html', {'books': []})


class AuthorGetOrCreateApiView(APIView):
    queryset = Author.objects.all()

    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        if not name:
            return Response('Author name not suplied', status=status.HTTP_400_BAD_REQUEST)

        author, created = Author.objects.get_or_create(name=name)

        serializer = AuthorSerializer(author)

        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class PublisherGetOrCreateApiView(APIView):
    queryset = Publisher.objects.all()

    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        if not name:
            return Response('Publisher name not suplied', status=status.HTTP_400_BAD_REQUEST)

        publisher, created = Publisher.objects.get_or_create(name=name)

        serializer = PublisherSerializer(publisher)

        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
