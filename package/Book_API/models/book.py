class Book:
    def __init__(self, id=None, title=None, author=None, isbn=None):
        self.id = id
        self.title = title
        self.author = author
        self.isbn = isbn
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn
        }