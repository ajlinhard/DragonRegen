import requests

class BookAPIClient:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url

    def get_all_books(self):
        """Retrieve all books"""
        response = requests.get(f'{self.base_url}/books')
        return response.json()

    def get_book(self, book_id):
        """Retrieve a specific book"""
        response = requests.get(f'{self.base_url}/books/{book_id}')
        return response.json()

    def create_book(self, book_data):
        """Create a new book"""
        response = requests.post(
            f'{self.base_url}/books', 
            json=book_data
        )
        return response.json()

    def update_book(self, book_id, book_data):
        """Update an existing book"""
        response = requests.put(
            f'{self.base_url}/books/{book_id}', 
            json=book_data
        )
        return response.json()

    def delete_book(self, book_id):
        """Delete a book"""
        response = requests.delete(f'{self.base_url}/books/{book_id}')
        return response.status_code == 204

# Example usage
def main():
    client = BookAPIClient()
    
    # Get all books
    print("All Books:", client.get_all_books())
    
    # Create a new book
    new_book = {
        "title": "Dune",
        "author": "Frank Herbert",
        "isbn": "9780441172719"
    }
    created_book = client.create_book(new_book)
    print("Created Book:", created_book)
    
    # Update the book
    updated_book = client.update_book(created_book['id'], {"title": "Dune: Updated"})
    print("Updated Book:", updated_book)
    
    # Delete the book
    client.delete_book(created_book['id'])

if __name__ == '__main__':
    main()