class BookService:
    def __init__(self):
        # In a real app, this would be a database connection
        self._books = [
            {
                'id': 1, 
                'title': 'To Kill a Mockingbird', 
                'author': 'Harper Lee',
                'isbn': '9780446310789'
            },
            {
                'id': 2, 
                'title': '1984', 
                'author': 'George Orwell',
                'isbn': '9780451524935'
            }
        ]
        self._next_id = len(self._books) + 1

    def get_all_books(self):
        return self._books

    def get_book_by_id(self, book_id):
        return next((book for book in self._books if book['id'] == book_id), None)

    def create_book(self, book_data):
        new_book = {
            'id': self._next_id,
            'title': book_data.get('title'),
            'author': book_data.get('author'),
            'isbn': book_data.get('isbn')
        }
        self._books.append(new_book)
        self._next_id += 1
        return new_book

    def update_book(self, book_id, book_data):
        book = self.get_book_by_id(book_id)
        if book:
            book.update({k: v for k, v in book_data.items() if v is not None})
        return book

    def delete_book(self, book_id):
        book = self.get_book_by_id(book_id)
        if book:
            self._books = [b for b in self._books if b['id'] != book_id]
            return True
        return False