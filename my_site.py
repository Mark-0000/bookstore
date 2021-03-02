from flask import Flask, redirect, url_for, render_template, request, session, flash
import pymongo
from bson.objectid import ObjectId

client = pymongo.MongoClient(
    "mongodb+srv://nine:root@nine-nfire.f9yn8.mongodb.net/bookstore?retryWrites=true&w=majority")
db = client['bookstore']
col_users = db['users']
col_books = db['books']

app = Flask(__name__)
app.secret_key = "A really really really really really really really really encrypted secret key one on Earth knows"


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/homey', methods=['POST', 'GET'])  # give path and method for the page using a decorator
def homey():  # create function to return page
    if request.method == 'POST':
        if 'update' in request.form:
            book_id = request.form['update']
            return redirect(url_for('update', _id=book_id))
        elif 'delete' in request.form:
            book_id = request.form['delete']
            # print(book_id)
            return redirect(url_for('delete', _id=book_id))
    else:
        if 'logged_in' in session:
            books = col_books.find()
            return render_template("index.html", current_user=session['current_user'], books=books)
        else:
            flash('You are not logged in!')
            return redirect(url_for('login'))


@app.route('/home', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        if 'update' in request.form:
            book_id = request.form['update']
            return redirect(url_for('update', _id=book_id))
        elif 'delete' in request.form:
            book_id = request.form['delete']
            # print(book_id)
            return redirect(url_for('delete', _id=book_id))
    else:
        if 'logged_in' in session:
            books = col_books.find().sort('title')
            return render_template("cards.html", current_user=session['current_user'], books=books)
        else:
            flash('You are not logged in!')
            return redirect(url_for('login'))


@app.route('/new', methods=['POST', 'GET'])  # give path for the page
def new():  # create function to return page
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        publisher = request.form['publisher']
        isbn = request.form['isbn']
        published_date = request.form['published_date']

        book = {
            'title': title,
            'author': author,
            'publisher': publisher,
            'isbn': isbn,
            'published_date': published_date
        }
        col_books.insert_one(book)
        flash('Book successfully added!')
        return redirect(url_for('new'))
    else:
        if 'logged_in' in session:
            return render_template("new.html", current_user=session['current_user'])
        else:
            flash('You are not logged in!')
            return redirect(url_for('login'))


@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        login_user = request.form['user_email']
        login_password = request.form['user_password']

        find_user = {'email': login_user}
        found_user = col_users.find(find_user)
        found_email = ''
        found_passwd = ''
        for user in found_user:
            found_email = user['email']
            found_passwd = user['password']

        if login_user == found_email and login_password == found_passwd:
            session['logged_in'] = True
            session['current_user'] = login_user
            return redirect(url_for('home'))
        else:
            flash('Invalid Email or Password!')
            return redirect(url_for('login'))
    else:
        if 'current_user' in session:
            return redirect(url_for('home'))
        else:
            return render_template("login.html")


@app.route('/create-user', methods=['POST', 'GET'])
def create_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        verify_password = request.form['verify_password']
        if password != verify_password:
            flash("Passwords doesn't match!")
            return redirect(url_for('create_user'))
        else:
            find_user = {'email': email}
            found_user = col_users.find(find_user)
            found_email = ''
            for user in found_user:
                found_email = user['email']

            if found_email == email:
                flash('Account already exists!')
                return redirect(url_for('create_user'))
            else:
                account = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'password': password
                }
                col_users.insert_one(account)
                flash('Account successfully created. Please login!')
                return redirect(url_for('login'))
    else:
        return render_template('create_user.html')


@app.route('/delete/<_id>')
def delete(_id):
    if 'logged_in' in session:
        book_id = _id
        to_delete = {
            '_id': ObjectId(book_id)
        }
        col_books.delete_one(to_delete)
        flash('Book deleted successfully!')
        return redirect(url_for('home'))
    else:
        flash('You are not logged in!')
        return redirect(url_for('login'))


@app.route('/update/<_id>', methods=['POST', 'GET'])
def update(_id):
    book_id = _id

    if request.method == 'POST':
        to_update = {
            '_id': ObjectId(book_id)
        }
        values = {'$set': {
            'title': request.form['title'],
            'author': request.form['author'],
            'publisher': request.form['publisher'],
            'isbn': request.form['isbn'],
            'published_date': request.form['published_date']
        }}
        col_books.update_one(to_update, values)
        flash('Book updated successfully!')
        return redirect(url_for('home'))
    else:
        if 'logged_in' in session:
            to_update = {
                '_id': ObjectId(book_id)
            }
            find_book = col_books.find(to_update)
            my_book = {}
            for book in find_book:
                my_book = book

            return render_template('update.html', current_user=session['current_user'], my_book=my_book)
        else:
            flash('You are not logged in!')
            return redirect(url_for('login'))


@app.route('/logout')
def logout():
    if 'logged_in' in session:
        flash('You have been logged out!')
    session.pop('current_user', None)
    session.pop('logged_in', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
