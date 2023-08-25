"""
Author: Karlgev
GitHub: https://github.com/Karlgev
Date: 08/25/23
"""

from flask import Flask, render_template, request
# run: pip install flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy

"""
This Flask application manages a collection of books, allowing users to add, edit, and delete book entries.
The app uses an SQLite database to store book information, including title, author, and rating.
Note: For user authentication, registration, and deployment, additional components and security measures are needed.
"""

# Create a Flask web application
app = Flask(__name__)

# List to store titles temporarily during rating editing
title_finder = []

# CREATE DATABASE
# CONFIGURATION: Setting up the database connection
# Configure the SQLite database URI for storing book data
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///new-books-collection.db"

# Create the SQLAlchemy extension to manage the database
db = SQLAlchemy()
# Initialize the Flask app with the SQLAlchemy extension
db.init_app(app)


# CREATE TABLE
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)

# Create table schema in the database. Requires application context.
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    # Fetch all books from the database
    with app.app_context():
        all_books = Book.query.all()
        return render_template("index.html", all_books=all_books)

@app.route('/delete/<string:author>/<string:title>')
def delete(author,title):
    # Delete a book by matching both author and title
    with app.app_context():
        book_to_delete = db.session.execute(db.select(Book).where(Book.title == title, Book.author == author)).scalar()
    db.session.delete(book_to_delete)
    db.session.commit()
    return "Data deleted successfully!"


@app.route('/edit/<string:author>/<string:rating>/<string:title>')
def edit(author, rating, title):
    # Fetch all books and render the edit template
    all_books = Book.query.all()
    title_finder.append(title)  # Store the title for later use
    return render_template("edit.html", author=author, rating=rating, title=title, all_books=all_books)


@app.route("/add")
def add():
    return render_template("add.html")


@app.route("/add/from_entry", methods=["POST"])
def receive_data():
    all_books = Book.query.all()
    if request.method == "POST":
        book_name = request.form.get('book_name')
        book_author = request.form.get('book_author')
        book_rating = request.form.get('book_rating')
        print(type(book_rating))  # Debug print

        # Data validation for new book entry
        if not book_name or not book_author or not is_valid_float(book_rating):
            return "Invalid data provided.", 400

        # Check for duplicate book title and valid rating range
        for book in all_books:
            if book.title == book_name:
                return "Book name exist"
            elif float(book_rating) > 100 or float(book_rating) < 0:
                return f"Book rating should be between 0 and 100. your rating was {book_rating}"

        # Add the new book to the database
        with app.app_context():
            new_book = Book(title=book_name, author=book_author, rating=book_rating)
            db.session.add(new_book)
            db.session.commit()

        return "Data received and added successfully!"
    else:
        return "Invalid method.", 405


@app.route('/edit/from_entry', methods=["POST"])
def edit_rating():
    if request.method == "POST":
        new_rating = request.form.get('new_rating')

        # Validate new_rating as a float
        try:
            new_rating = float(new_rating)
            if new_rating > 100:
                return f"Invalid rating entry should not exceed 100. your rating was {new_rating}", 400
            elif new_rating < 0:
                return f"Invalid rating entry should not be less then 0. your rating was {new_rating}", 400
        except ValueError:
            return "Invalid rating format.", 400

        # Update the book's rating
        with app.app_context():
            book_to_update = db.session.execute(db.select(Book).where(Book.title == title_finder[0])).scalar()
            if book_to_update:
                book_to_update.rating = new_rating
                db.session.commit()
                title_finder.pop(0)
        return "Rating updated successfully!"
    else:
        return "Book not found."


# HELPER FUNCTION: Validate if a string can be converted to a float
def is_valid_float(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

# Run the app in debug mode
if __name__ == "__main__":
    app.run(debug=True)

