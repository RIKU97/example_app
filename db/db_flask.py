
'''
1search book w/o isdn
2search user
3search rental
4search book AND rental/rental_date,return_date 
5add book
6delete book
7add user
8delete user
9add rental
10 search book based on genre
11 search book based on publish_date 
12 search book based on sql.like
'''



'''
from flask import Flask, request, jsonify, g, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)
app.json.ensure_ascii = False

dbpath = 'library.db'  

def get_db():  
    db = getattr(g, '_database', None)
    return db 

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
'''
#get all books without isbn
'''
@app.route('/search_books', methods=['GET'])
def get_books():
    try:
        con = get_db() 
        con.row_factory = sqlite3.Row 
        cur = con.cursor()
        
        cur.execute('SELECT title, genre, author, publish_date, publisher, amount FROM books')
        books = [dict(row) for row in cur.fetchall()]
        
        return render_template("search_book.html", book_lists=books)
    except sqlite3.Error as e:
        #erroy対応
        return jsonify({"error": str(e)}), 500
'''

#get all users
'''
@app.route('/search_users', methods=['GET'])
def get_users():
    try:
        con = get_db() 
        con.row_factory = sqlite3.Row 
        cur = con.cursor()
        
        cur.execute('SELECT * FROM users')
        users = [dict(row) for row in cur.fetchall()]
        
        return render_template("search_user.html", user_lists=users)
    except sqlite3.Error as e:
        #erroy対応
        return jsonify({"error": str(e)}), 500
'''

#get all rental
'''
@app.route('/search_rental', methods=['GET'])
def get_rental():
    try:
        con = get_db() 
        con.row_factory = sqlite3.Row 
        cur = con.cursor()
        
        cur.execute('SELECT * FROM rental')
        rental = [dict(row) for row in cur.fetchall()]
        
        return render_template("search_rental.html", rental_list=rental)
    except sqlite3.Error as e:
        #erroy対応
        return jsonify({"error": str(e)}), 500
'''

#get all book AND rental date,return date
'''
@app.route('/book_rentals', methods=['GET'])
def get_book_rentals():
    try:
        con = get_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        cur.execute('
            SELECT title, genre, author, publish_date, publisher, amount, rental_date, return_date
            FROM books
            INNER JOIN rentals ON books.isbn = rentals.book_id
        ')       
        book_rentals = [dict(row) for row in cur.fetchall()]
        
        return render_template("book_rentals.html", book_rental_lists=book_rentals)
    except sqlite3.Error as e:
        #erroy対応
        return jsonify({"error": str(e)}), 500
'''

#add book
'''
@app.route('/add_books', methods=['POST'])
def add_book():
    try:
        con = get_db()
        cur = con.cursor()
        
        isbn = request.form["isbn"]
        title = request.form["title"]
        genre = request.form["genre"]
        author = request.form["author"]
        publisher = request.form["publisher"]
        publish_date = request.form["publish_date"]
        
        
        cur.execute('INSERT INTO books (isbn, title, genre, author, publisher,publish_date,amount) 
                    VALUES ('{isbn}','{title}','{genre}','{author}','{publish_date}','{publisher}',1))
        con.commit()
        
        return jsonify({"message": "Book added successfully"}), 201
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
'''

# delete book
'''
@app.route('/books/<int:isbn>', methods=['DELETE'])
def delete_book(isbn):
    try:
        con = get_db()
        cur = con.cursor()
        
        cur.execute('DELETE FROM books WHERE isbn = ?', (isbn,))
        con.commit()

        return jsonify({"message": "Book deleted successfully"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
'''

#add user
'''
@app.route('/add_users', methods=['POST'])
def add_user():
    try:
        con = get_db()
        cur = con.cursor()
        
        userid = request.form["userid"]
        name = request.form["name"]
        
        
        cur.execute('INSERT INTO users (name, major)VALUES('{userid}','{name}'))
        con.commit()
        
        return jsonify({"message": "User added successfully"}), 201
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500
'''

# delete user
'''
@app.route('/users/<int:isbn>', methods=['DELETE'])
def delete_book(userid):
    try:
        con = get_db()
        cur = con.cursor()
        
        cur.execute('DELETE FROM users WHERE userid = ?', (userid,))
        con.commit()

        return jsonify({"message": "User deleted successfully"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
'''

# add rental
'''
@app.route('/add_rentals', methods=['POST'])
def add_rental(rentals_amount):  #outside the add_rental , there should be a rentals_amount to record the amounts of rentals.
    try:
        con = get_db()
        cur = con.cursor()
        
        cur.execute('SELECT amount FROM books WHERE isbn = ?', (isbn,))
        book = cur.fetchone()
        
        if book is None:
            return jsonify({"message": "Book not found"}), 404
        
        amount = book['amount']
        
        if amount > 0:
            new_amount = amount - 1
            rentals_amount=rentals_amount+1
            
            rental_data = request.get_json()
            rentalid=rentals_amount
            userid = rental_data.get('user_id')
            isbn = rental_data.get('isbn')
            rental_date = rental_data.get('rental_date')
            return_date = rental_data.get('return_date')
            
            
            cur.execute('UPDATE books SET amount = ? WHERE isbn = ?', (new_amount, book_id))
            cur.execute('INSERT INTO rentals (rentalid,userid, isbn, rental_date, return_date) VALUES (?,?, ?, ?, ?)', 
                        (rentals_amount,userid, isbn, rental_date, return_date))
            con.commit()
            return rentals_amount,jsonify({"message": "Rental added successfully"}), 201
        else:
            return rentals_amount,jsonify({"message": "No more book available for rental"}), 400
        
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500
 '''
 
 
 # search book as genre
'''
@app.route('/books/genre/<string:genre>', methods=['GET'])
def get_books_by_genre(genre):
    try:
        con = get_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        
        cur.execute('SELECT * FROM books WHERE genre = ?', (genre,))
        books = [dict(row) for row in cur.fetchall()]
        
        return jsonify(books), 200
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
'''


 # search book as publish date
'''
@app.route('/books/publishdate/<string:publishdate>', methods=['GET'])
def get_books_by_publishdate(publishdate):
    try:
        con = get_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        
        cur.execute('SELECT * FROM books WHERE publishdate = ?', (publishdate,))
        books = [dict(row) for row in cur.fetchall()]
        
        return jsonify(books), 200
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
'''

# retrieval
'''
@app.route('/books/retrieval', methods=['GET'])
def retrieve_books():
    try:
        query = request.args.get('q', '')
        
        con = get_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        
        cur.execute('SELECT * FROM books WHERE title LIKE ?', ('%' + query + '%',))
        books = [dict(row) for row in cur.fetchall()]
        
        return jsonify(books), 200
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
'''
