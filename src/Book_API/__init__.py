from .models import Book
from .services.book_service import BookService
from .resources.book_resources import BookListResource, BookResource
from .app import create_app