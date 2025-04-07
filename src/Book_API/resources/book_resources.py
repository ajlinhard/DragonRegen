from flask import request, jsonify
from flask_restful import Resource
# There is an issue when running app.py vs pytest where the path requres no "." in front of the path and then requires 2 "." in front of the path
from Book_API.services.book_service import BookService

# Do this to make the book list data persistent until app is closed/restarted
book_service = BookService()

class BookListResource(Resource):
    def __init__(self):
        self.book_service = book_service

    def get(self):
        """Retrieve all books"""
        books = self.book_service.get_all_books()
        return books

    def post(self):
        """Create a new book"""
        print('here')
        print(request)
        print(request.json)
        print(request.data)
        print('done')
        book_data = request.json
        new_book = self.book_service.create_book(book_data)
        return new_book, 201

class BookResource(Resource):
    def __init__(self):
        self.book_service = book_service

    def get(self, book_id):
        """Retrieve a specific book by ID"""
        book = self.book_service.get_book_by_id(book_id)
        if book:
            return book
        return {'message': 'Book not found'}, 404

    def put(self, book_id):
        """Update a specific book"""
        book_data = request.json
        updated_book = self.book_service.update_book(book_id, book_data)
        if updated_book:
            return jsonify(updated_book)
        return {'message': 'Book not found'}, 404

    def delete(self, book_id):
        """Delete a specific book"""
        success = self.book_service.delete_book(book_id)
        if success:
            return '', 204
        return {'message': 'Book not found'}, 404