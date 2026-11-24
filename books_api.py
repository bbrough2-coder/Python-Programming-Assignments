
# Name: Brianna Hubble
# File Name: books_api.py
# Description: A REST API that allows users to create, read,
# update, and delete books using Flask and SQLite.

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Create the Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'book_name': self.book_name,
            'author': self.author,
            'publisher': self.publisher
        }


# READ: Get all books
@app.route('/books', methods=['GET'])
def get_books():
    books = db.session.execute(
        db.select(Book).order_by(Book.id)
    ).scalars().all()

    return jsonify({'books': [book.to_dict() for book in books]})


# READ: Get one book by ID
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = db.session.get(Book, book_id)

    if book is None:
        return jsonify({'error': 'Book not found'}), 404

    return jsonify(book.to_dict())


# CREATE: Add a new book
@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({'error': 'Please provide JSON data'}), 400

    required_fields = ['book_name', 'author', 'publisher']

    if not all(data.get(field) for field in required_fields):
        return jsonify({
            'error': 'Book name, author, and publisher are required'
        }), 400

    new_book = Book(
        book_name=data['book_name'],
        author=data['author'],
        publisher=data['publisher']
    )

    db.session.add(new_book)
    db.session.commit()

    return jsonify({
        'message': 'Book successfully added',
        'book': new_book.to_dict()
    }), 201


# UPDATE: Update an existing book
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = db.session.get(Book, book_id)

    if book is None:
        return jsonify({'error': 'Book not found'}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({'error': 'Please provide JSON data'}), 400

    allowed_fields = ['book_name', 'author', 'publisher']

    if not data or any(field not in allowed_fields for field in data):
        return jsonify({'error': 'Please provide valid book information'}), 400

    for field in allowed_fields:
        if field in data:
            if not isinstance(data[field], str) or not data[field].strip():
                return jsonify({'error': f'{field} must be a non-empty string'}), 400
            setattr(book, field, data[field].strip())

    db.session.commit()

    return jsonify({
        'message': 'Book successfully updated',
        'book': book.to_dict()
    })


# DELETE: Remove a book
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = db.session.get(Book, book_id)

    if book is None:
        return jsonify({'error': 'Book not found'}), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({'message': 'Book successfully deleted'})


# Create the database tables and start the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
