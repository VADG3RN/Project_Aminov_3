from django import forms
from .models import Book
import json

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'year', 'pages', 'genre', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year < 1000 or year > 2030:
            raise forms.ValidationError("Введите корректный год издания")
        return year
    
    def clean_pages(self):
        pages = self.cleaned_data.get('pages')
        if pages <= 0:
            raise forms.ValidationError("Количество страниц должно быть положительным числом")
        return pages

class JSONUploadForm(forms.Form):
    json_file = forms.FileField(
        label="Выберите JSON файл",
        help_text="Файл должен быть в формате JSON"
    )