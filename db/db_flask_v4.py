
'''
1search book w/o isdn
2search user
3search rental
4search book AND rental/rental_date,return_date 
5add book
#6delete book     必要がないと思う
7add user
8delete user
9add rental
#10 search book based on genre    必要がないと思う
#11 search book based on publish_date     必要がないと思う
12 search book based on book_name(sql.like)
13 search book
#14 search rental based on userid  必要がないと思う
15 admin確認
16 init_db
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

#1 get all books without isbn
'''
#ユーザホーム->一覧取得　/(username)_home/book_list
@app.route('/search_books', methods=['GET'])
def get_books():　
    try:
        con = get_db() 
        con.row_factory = sqlite3.Row 
        cur = con.cursor()
        
        cur.execute('SELECT title, genre, author, publish_date, publisher FROM books')
        books = [dict(row) for row in cur.fetchall()]
        
        return render_template("search_books.html", book_lists=books)
    except sqlite3.Error as e:
        #erroy対応
        return jsonify({"error": str(e)}), 500
'''

#2 get all users
'''
#管理者ホーム->ユーザ確認　　/admin_home/users
@app.route('/search_users', methods=['GET'])
def get_users():
    try:
        con = get_db() 
        con.row_factory = sqlite3.Row 
        cur = con.cursor()
        
        cur.execute('SELECT userid,name FROM users WHERE admin_flag = 0')
        users = [dict(row) for row in cur.fetchall()]
        
        return render_template("search_user.html", user_lists=users)
    except sqlite3.Error as e:
        #erroy対応
        return jsonify({"error": str(e)}), 500
'''

#3 get all rental
'''
#管理者ホームの貸出履歴一覧　　/admin_home
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


#4 get all book AND rental date,return date
'''
#ユーザホーム->貸出履歴一覧　　/(username)_home
@app.route('/(username)_home', methods=['GET'])
def get_book_rentals_base_userid(userid):
    try:
        con = get_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        cur.execute('
            SELECT title, genre, author, publish_date, publisher, rental_date, return_date
            FROM books
            INNER JOIN rentals ON books.isbn = rentals.isbn
            WHERE userid=?',(userid,))       
        book_rentals = [dict(row) for row in cur.fetchall()]
        
        return render_template("book_rentals.html", book_rental_lists=book_rentals)
    except sqlite3.Error as e:
        #erroy対応
        return jsonify({"error": str(e)}), 500
'''

#5 add book
'''
#管理者ホーム->在庫追加　　/admin_home/book_inventory
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
        
        cur.execute('INSERT INTO books (isbn, title, genre, author, publisher,publish_date,ava_flag) 
                    VALUES ('{isbn}','{title}','{genre}','{author}','{publish_date}','{publisher}',1))
        con.commit()
        
        return jsonify({"message": "Book added successfully"}), 201
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
'''

#6 delete book
'''
#管理者ホーム->在庫削除　　/admin_home/book_inventory
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

#7 add user
'''
#管理者ホーム->ユーザ追加　　/admin_home/users
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

#8 delete user
'''
#管理者ホーム->ユーザ削除　　/admin_home/users
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

#9 add rental
'''
#ユーザホーム->貸出　　/(username)_home/book_list
@app.route('/add_rentals', methods=['POST'])
def add_rental():  
    try:
        con = get_db()
        cur = con.cursor()
        isbn = request.form["isbn"]
        
        cur.execute('SELECT MAX(rentalid) FROM rentals')　#rentalidを取る
        max_rentalid = cur.fetchone()[0]
        if max_rentalid is None:
            rentalid = 1
        else:
            rentalid = max_rentalid + 1
        
        cur.execute('SELECT amount FROM books WHERE isbn = ?', (isbn,))   ＃貸出可能を確認
        book = cur.fetchone()    
        ava_flag = book['ava_flag']
        
        if ava_flag > 0:
            ava_flag = ava_flag - 1     
            rental_data = request.get_json()
            userid = rental_data.get('userid')
            rental_date = rental_data.get('rental_date')
            return_date = rental_data.get('return_date')
            
            
            cur.execute('UPDATE books SET ava_flag = ? WHERE isbn = ?', (ava_flag, isbn))
            cur.execute('INSERT INTO rentals (rentalid,userid, isbn, rental_date) VALUES (?,?, ?, ?)', 
                        (rentalid,userid, isbn, rental_date))
            con.commit()
            return jsonify({"message": "貸出中"}), 201
        else:
            return jsonify({"message": "貸出不可"}), 400
        
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500
 '''
 
 
 #10 search book as genre
'''
#ユーザホーム->一覧取得(genre base)　　/(username)_home/book_list
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


 #11 search book as publish date
'''
#ユーザホーム->一覧取得(date base)　　/(username)_home/book_list
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

#12 retrieval
'''
#ユーザホーム->一覧取得(book name base)　　/(username)_home/book_list
@app.route('/books/retrieval', methods=['GET'])
def retrieve_books():
    try:
        query = request.args.get('q', '')
        
        con = get_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        
        cur.execute('SELECT title, genre, author, publish_date, publisher FROM books WHERE title LIKE ?', ('%' + query + '%',))
        books = [dict(row) for row in cur.fetchall()]
        
        return jsonify(books), 200
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
'''


#13 get all books
'''
#管理者ホーム->在庫確認　　/admin_home/book_inventory
@app.route('/search_all_books', methods=['GET'])
def get_books():
    try:
        con = get_db() 
        con.row_factory = sqlite3.Row 
        cur = con.cursor()
        
        cur.execute('SELECT * FROM books')
        books = [dict(row) for row in cur.fetchall()]
        
        return render_template("search_all_books.html", book_lists=books)
    except sqlite3.Error as e:
        #erroy対応
        return jsonify({"error": str(e)}), 500
'''

 #14 search rental based on userid
'''
#ユーザホームの貸出履歴表示　　/(username)_home
@app.route('/search_rental/<string:userid>', methods=['GET'])
def search_rental_based_on_userid(userid):
    try:
        con = get_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        
        cur.execute('SELECT * FROM rentals WHERE userid = ?', (userid,))
        rentals = [dict(row) for row in cur.fetchall()]
        
        return jsonify(rentals), 200
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
'''
#15 admin確認
'''
def is_admin(userid):
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute('SELECT admin_flag FROM users WHERE userid = ?', (userid,))
        result = cur.fetchone()
        conn.close()
        
        if result and result['admin_flag'] == 1:
            return True
        else:
            return False
    
    except Exception as e:
        print(f"Error checking admin status: {str(e)}")
        return False
'''

#16 init_db
'''
def init_db():
    conn = sqlite3.connect(book_db)
    cursor = conn.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS books (isbn TEXT NOT NULL, title TEXT NOT NULL, genre TEXT, author TEXT, publisher TEXT, publish_date DATE, ava_flag INTEGER DEFAULT 1, PRIMARY KEY(isbn))')
    cursor.execute('CREATE TABLE IF NOT EXISTS major_name (majorid INTEGER NOT NULL, majorname TEXT, PRIMARY KEY(majorid))')
    cursor.execute('CREATE TABLE IF NOT EXISTS rentals (rentalid INTEGER NOT NULL, userid TEXT NOT NULL, isbn TEXT NOT NULL, rental_date DATE, return_date DATE, PRIMARY KEY(rentalid))')
    cursor.execute('CREATE TABLE IF NOT EXISTS student_major (userid TEXT NOT NULL, majorid INTEGER, PRIMARY KEY(userid))')
    cursor.execute('CREATE TABLE IF NOT EXISTS users (userid TEXT NOT NULL, name TEXT NOT NULL, admin_flag INTEGER DEFAULT 0, PRIMARY KEY(userid))')

    cursor.execute('INSERT OR IGNORE INTO users (userid, name, admin_flag) VALUES ("admin", "管理者", 1)')

    conn.commit()
    conn.close()
'''