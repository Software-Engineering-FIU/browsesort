from datetime import datetime
from flask_marshmallow import Marshmallow
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(80), nullable=False, unique=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.String(120), unique=True)
    price = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(15), nullable=False)
    publisher = db.Column(db.String(20))
    year_published = db.Column(db.Date)
    copies_sold = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    reviews = db.relationship('Review', backref='book_reviewed', lazy=True)
    avg_rating = db.Column(db.Integer)

    def __repr__(self):
        return f"Book('{self.name}', '{self.author}','{self.genre}', '{self.price}', '{self.copies_sold}')"


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(15), nullable=False)
    last_name = db.Column(db.String(15), nullable=False)
    biography = db.Column(db.String(120), unique=True)
    publisher = db.Column(db.String(20))
    books_written = db.relationship('Book', backref='author')

    def __repr__(self):
        return f"Author('{self.last_name}', '{self.first_name}')"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password =  db.Column(db.String(8), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    name = db.Column(db.String(120), unique=True)
    home_address = db.Column(db.String(120), unique=True)
    reviews = db.relationship('Review', backref='review_author', lazy=True)

    def __str__(self):
        return self.username


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer(), nullable=False)
    date_posted = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    comment = db.Column(db.Text)
    book_id = db.Column(db.String(120), db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Review('{self.username}', '{self.email}', '{self.rating}', '{self.comment}', '{self.date}')"


# Book schema
class BookDetailSchema(ma.Schema):
    class Meta:
        model = Book
        fields = ("name", 'isbn', 'genre', 'copies_sold', 'avg_rating')


book_schema = BookDetailSchema()
books_schema = BookDetailSchema(many=True)


# User schema
class UserDetailSchema(ma.Schema):
    class Meta:
        model = User
        fields = ("username", 'email')


user_schema = UserDetailSchema()
users_schema = UserDetailSchema(many=True)


@app.route('/')
def home():
    return 'Hello there!'


# shows all users
@app.route('/users')
def users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)


# shows all books
@app.route('/books')
def books():
    all_books = Book.query.all()
    result = books_schema.dump(all_books)
    return jsonify(result)


# filters by genre
@app.route('/books/filter_by_genre/<usergenre>', methods=['GET'])
def filterGenre(usergenre):
    filter_genre = Book.query.filter_by(genre=usergenre).all()
    return jsonify(books_schema.dump(filter_genre))


# filter by top sellers
@app.route('/books/filter_by_sold/<int:sold>', methods=['GET'])
def filterTopSold(sold):
    filter_sold = Book.query.order_by(desc(Book.copies_sold)).limit(sold)
    return jsonify(books_schema.dump(filter_sold))


# filter by rating, need book average ratings
@app.route('/books/filter_by_rating/<float:rating>', methods=['GET'])
def bookRating(rating):
    filter_rating = Book.query.filter(Book.avg_rating >= rating).all()
    return jsonify(books_schema.dump(filter_rating))


@app.route('/books/show_list/<int:x>', methods=['GET'])
def getList(x):
    filter_amount = Book.query.limit(x).all()
    return jsonify(books_schema.dump(filter_amount))


if __name__ == '__main__':
    app.run(debug=True)