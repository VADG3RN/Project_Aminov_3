from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/form/', views.book_form, name='book_form'),
    path('book/upload/', views.upload_json, name='upload_json'),
    path('book/list/', views.book_list, name='book_list'),
    path('book/json-files/', views.json_files_list, name='json_files_list'),
    path('book/export/', views.export_books_json, name='export_books_json'),
]