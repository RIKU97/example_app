from flask import Flask,request,jsonify,g,render_template,redirect,url_for
import json
import sqlite3
import json   


app = Flask(__name__)
app.json.ensure_ascii = False   # 文字化けを防ぐ

dbpath = 'DATABASE.db' #テーブルを保存するファイル

def get_db():#データベースのコネクションを取得
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(dbpath)
        db.execute('CREATE TABLE IF NOT EXISTS books(isbn integer primary key, title VARCHAR(100), genre VARCHAR(100), author VARCHAR(100), publish_date VARCHAR(140), publisher VARCHAR(100),amount integer)')
    return db 



# ログイン画面表示
@app.route('/login',methods=['GET'])
def show_login():
    return render_template('login.html')


# 管理者トップ画面表示
@app.route('/admin',methods=['GET'])
def show_admin():
    return render_template('admin_home.html')

@app.route('/admin/books')
def book_management():
    return redirect(url_for('show_register'))

@app.route('/admin/users')
def user_management():
    return render_template('register_user.html')

@app.route('/admin/loans')
def rent_list():
    return render_template('rent_list.html')

# ログイン認証
@app.route('/login/request',methods=['POST'])
def process_login():
    user_id = request.form["userId"]
    if user_id == "admin":
        return redirect(url_for('show_admin'))
    else:
        return redirect(url_for('get_books'))


# 本一覧GETに対する処理
@app.route('/search', methods=['GET'])
def get_books():
    con = get_db() 
    con.row_factory = sqlite3.Row 
    cur = con.cursor()
              
    cur.execute('SELECT * FROM books')
    lists = []
    for row in cur.fetchall(): 
        lists.append(dict(row))
            
    return render_template("search_book.html",book_lists=lists)

    


@app.route('/register',methods=['GET'])
def show_register():
    con = get_db() 
    con.row_factory = sqlite3.Row 
    cur = con.cursor()
              
    cur.execute('SELECT * FROM books')
    lists = []
    for row in cur.fetchall(): 
        lists.append(dict(row))

    return render_template("register_book.html",book_lists=lists)





# 本登録の処理
@app.route('/register/post', methods=['POST'])
def register():
    con = get_db() 
    cur = con.cursor() 
            
    isbn = request.form["isbn"]
    title = request.form["title"]
    genre = request.form["genre"]
    author = request.form["author"]
    publisher = request.form["publisher"]
    publish_date = request.form["publish_date"]
    
    try:
        cur.execute(f"INSERT INTO books(isbn,title,genre,author,publish_date,publisher,amount) values({isbn},'{title}','{genre}','{author}','{publish_date}','{publisher}',1)") 
        con.commit()
    except:
        return "register error"

    return redirect(url_for('show_register'))




if __name__ == "__main__":
    app.run()
