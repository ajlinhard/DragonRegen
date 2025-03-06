from flask import request, jsonify
from flask_restful import Resource
from services.book_service import BookService

class BookListResource(Resource):
    def __init__(self):
        self.book_service = BookService()

    def get(self):
        """Retrieve all books"""
        books = self.book_service.get_all_books()
        return jsonify(books)

    def post(self):
        """Create a new book"""
        book_data = request.json
        new_book = self.book_service.create_book(book_data)
        return jsonify(new_book), 201

class BookResource(Resource):
    def __init__(self):
        self.book_service = BookService()

    def get(self, book_id):
        """Retrieve a specific book by ID"""
        book = self.book_service.get_book_by_id(book_id)
        if book:
            return jsonify(book)
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