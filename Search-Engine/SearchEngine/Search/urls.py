from django.urls import path
from . import views

urlpatterns=[
    path("home/",views.home,name="home"),
    path("word/",views.input_word,name="word"),
]
