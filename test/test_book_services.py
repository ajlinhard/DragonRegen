# Creating test for book api BookService class
import pytest
# from Book_API.services.book_service import BookService
from services.book_service import BookService

class TestBookService:
    @pytest.fixture
    def book_service(self):
        """Create a fresh BookService instance for each test."""
        return BookService()
    
    def test_get_all_books(self, book_service):
        """Test that get_all_books returns all books."""
        books = book_service.get_all_books()
        assert len(books) == 2
        assert books[0]['title'] == 'To Kill a Mockingbird'
        assert books[1]['title'] == '1984'
    
    def test_get_book_by_id_existing(self, book_service):
        """Test retrieving an existing book by ID."""
        book = book_service.get_book_by_id(1)
        assert book is not None
        assert book['title'] == 'To Kill a Mockingbird'
        assert book['author'] == 'Harper Lee'