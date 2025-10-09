import os
import json
import uuid
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError
from .models import Book
from .forms import BookForm, JSONUploadForm

def home(request):
    """Главная страница"""
    return render(request, 'myapp3/home.html')

def book_form(request):
    """Форма для ввода данных о книге"""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            
            # Сохраняем в JSON файл
            save_book_to_json(book)
            
            return redirect('book_list')
    else:
        form = BookForm()
    
    return render(request, 'myapp3/book_form.html', {'form': form})

def save_book_to_json(book):
    """Сохраняет книгу в JSON файл"""
    books_dir = os.path.join(settings.BASE_DIR, 'books_data')
    
    # Создаем папку если не существует
    if not os.path.exists(books_dir):
        os.makedirs(books_dir)
    
    # Генерируем уникальное имя файла
    filename = f"book_{uuid.uuid4().hex[:8]}.json"
    file_path = os.path.join(books_dir, filename)
    
    # Сохраняем данные в JSON
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(book.to_dict(), f, ensure_ascii=False, indent=2)
    
    return file_path

def upload_json(request):
    """Загрузка JSON файлов"""
    if request.method == 'POST':
        form = JSONUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['json_file']
            
            # Проверяем расширение файла
            if not uploaded_file.name.lower().endswith('.json'):
                form.add_error('json_file', 'Файл должен иметь расширение .json')
                return render(request, 'myapp3/upload_json.html', {'form': form})
            
            # Генерируем безопасное имя файла
            safe_filename = f"uploaded_{uuid.uuid4().hex[:8]}.json"
            upload_dir = os.path.join(settings.BASE_DIR, 'books_data')
            
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            file_path = os.path.join(upload_dir, safe_filename)
            
            try:
                # Сохраняем файл
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                # Проверяем валидность JSON
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                # Проверяем структуру данных
                if not validate_book_json(json_data):
                    os.remove(file_path)  # Удаляем невалидный файл
                    form.add_error('json_file', 'Неверная структура JSON файла')
                    return render(request, 'myapp3/upload_json.html', {'form': form})
                
                # Сохраняем книгу в базу данных
                book = Book(
                    title=json_data.get('title', ''),
                    author=json_data.get('author', ''),
                    year=json_data.get('year', 0),
                    pages=json_data.get('pages', 0),
                    genre=json_data.get('genre', ''),
                    description=json_data.get('description', '')
                )
                book.full_clean()  # Валидация модели
                book.save()
                
                return redirect('book_list')
                
            except json.JSONDecodeError:
                if os.path.exists(file_path):
                    os.remove(file_path)
                form.add_error('json_file', 'Файл содержит невалидный JSON')
            except ValidationError as e:
                if os.path.exists(file_path):
                    os.remove(file_path)
                form.add_error('json_file', f'Ошибка валидации данных: {e}')
            except Exception as e:
                if os.path.exists(file_path):
                    os.remove(file_path)
                form.add_error('json_file', f'Ошибка при обработке файла: {e}')
    
    else:
        form = JSONUploadForm()
    
    return render(request, 'myapp3/upload_json.html', {'form': form})

def validate_book_json(data):
    """Проверяет валидность структуры JSON данных книги"""
    required_fields = ['title', 'author', 'year', 'pages']
    
    if not isinstance(data, dict):
        return False
    
    for field in required_fields:
        if field not in data:
            return False
    
    # Проверяем типы данных
    if not isinstance(data['title'], str) or not data['title'].strip():
        return False
    if not isinstance(data['author'], str) or not data['author'].strip():
        return False
    if not isinstance(data['year'], int) or data['year'] < 1000:
        return False
    if not isinstance(data['pages'], int) or data['pages'] <= 0:
        return False
    
    return True

def book_list(request):
    """Список всех книг из базы данных"""
    books = Book.objects.all().order_by('title')
    return render(request, 'myapp3/book_list.html', {'books': books})

def json_files_list(request):
    """Показывает все JSON файлы и их содержимое"""
    books_dir = os.path.join(settings.BASE_DIR, 'books_data')
    json_files_data = []
    
    if not os.path.exists(books_dir):
        message = "Папка с JSON файлами не существует"
    else:
        json_files = [f for f in os.listdir(books_dir) if f.endswith('.json')]
        
        if not json_files:
            message = "Нет доступных JSON файлов"
        else:
            message = None
            for filename in json_files:
                file_path = os.path.join(books_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = json.load(f)
                    
                    json_files_data.append({
                        'filename': filename,
                        'content': file_content,
                        'file_size': os.path.getsize(file_path)
                    })
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    json_files_data.append({
                        'filename': filename,
                        'error': f'Ошибка чтения файла: {str(e)}',
                        'file_size': os.path.getsize(file_path)
                    })
    
    return render(request, 'myapp3/json_files_list.html', {
        'json_files': json_files_data,
        'message': message
    })

def export_books_json(request):
    """Экспортирует все книги в один JSON файл"""
    books = Book.objects.all()
    books_data = [book.to_dict() for book in books]
    
    response = HttpResponse(
        json.dumps(books_data, ensure_ascii=False, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = 'attachment; filename="all_books.json"'
    
    return response