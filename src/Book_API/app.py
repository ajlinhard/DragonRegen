from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from Book_API.resources.book_resources import BookListResource, BookResource

def create_app():
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_MIMETYPE'] = 'application/json'
    CORS(app)
    api = Api(app)

    # Register API routes
    api.add_resource(BookListResource, '/books')
    api.add_resource(BookResource, '/books/<int:book_id>')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)