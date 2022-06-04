from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/authors/get_or_create', views.AuthorGetOrCreateApiView.as_view()),
    path('api/publishers/get_or_create', views.PublisherGetOrCreateApiView.as_view()),
]
