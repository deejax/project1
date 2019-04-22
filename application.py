import os
import requests

from flask import Flask, session ,render_template, request ,redirect, url_for ,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.secret_key = "!§$$&--a@°^-he he"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# its only usable inside context, i.e. flask is running -> session['username']=None
# ->session['logged_in'] = False

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Loading the main page
@app.route("/" , methods=["POST" , "GET"])
def index():
        book_list=[]
        if 'username' in session:
            user = session['username']
        else:
            user = None

        search = request.form.get("search")

        if search:
            log="SEARCH : User : "+user+" & Keyword: "+search
            db.execute("INSERT INTO d_book.syslog (log_text) VALUES (:log)",
            {"log": log})
            db.commit()
            book_list=db.execute("SELECT isbn , title , author , year FROM d_book.books WHERE isbn like  :sid or author like :sid or title like :sid union SELECT isbn , title , author ,year FROM d_book.books WHERE isbn like  :csid or author like :csid or title like :csid ", {"sid": "%"+search+"%" , "csid":"%"+search.capitalize()+"%"}).fetchall()
            if book_list:
                for isbn , title , author , year in book_list:
                        log="ISBN: "+isbn+" Title: "+title+" Author: "+author+" Year: "+year
                        db.execute("INSERT INTO d_book.syslog (log_text) VALUES (:log)",
                        {"log": log})
                        db.commit()
            else:
                log="NO RESULT"
                db.execute("INSERT INTO d_book.syslog (log_text) VALUES (:log)",
                {"log": log})
                db.commit()
            log="END SEARCH"
            db.execute("INSERT INTO d_book.syslog (log_text) VALUES (:log)",
            {"log": log})
            db.commit()
        return render_template("index.html" ,user=user ,book_list=book_list)

@app.route("/user_nav" , methods=["POST" , "GET"])
def user_nav():
    if request.method == 'POST':
        but_act = request.form.get("but_act")
        error=""
    if but_act== "Sign Out":
        # Logging out the user
        user_id=session['username']
        log="LOGGED OUT : User : "+ user_id
        db.execute("INSERT INTO d_book.syslog (log_text) VALUES (:log)",
        {"log": log})
        db.commit()
        session.pop('username', None)
        return redirect(url_for("index"))
    elif but_act== "Sign In":
        return render_template("auth.html" , reg_flag ="N", error=error)
    elif but_act =="Sign Up" :
        #error = "Some error text"
        return render_template("auth.html" , reg_flag ="Y", error=error)

@app.route("/user_auth" , methods=["POST" , "GET"])
def user_auth():
    user_id = request.form.get("user_id")
    user_pwd = request.form.get("user_pwd")
    but_act = request.form.get("but_act")
    if but_act== "Sign In":
        reg_flag ="N"
    elif but_act== "Sign Up":
        reg_flag ="Y"

    if not user_id:
        error ="User ID cannot be blanks"
        return render_template("auth.html" , error=error)
    if not user_pwd:
        error ="Password cannot be blanks"
        return render_template("auth.html" ,  error=error)

    if reg_flag =="N":
        if db.execute("SELECT * FROM d_book.user WHERE user_id = :uid and password=:pwd", {"uid": user_id , "pwd":user_pwd}).rowcount == 0:
            error ="Invalid User or Password"
            log="INVALID TRY: User : "+user_id+" & Password : "+user_pwd
            db.execute("INSERT INTO d_book.syslog (log_text) VALUES (:log)",
            {"log": log})
            db.commit()
            return render_template("auth.html" ,  error=error)
        else:
            session['logged_in'] = True
            session['username'] = user_id
            log="LOGGED IN : User : "+user_id+" & Password : "+user_pwd
            db.execute("INSERT INTO d_book.syslog (log_text) VALUES (:log)",
            {"log": log})
            db.commit()
            return redirect(url_for("index"))


    if reg_flag =="Y" :
        if db.execute("SELECT * FROM d_book.user WHERE user_id = :uid", {"uid": user_id}).rowcount != 0:
            error ="User already exists"
            log="EXISTING USER CREATE TRY: User : "+user_id+" & Password : "+user_pwd
            db.execute("INSERT INTO d_book.syslog (log_text) VALUES (:log)",
            {"log": log})
            db.commit()
            return render_template("auth.html" ,  error=error)
        else:
            db.execute("INSERT INTO d_book.user (user_id, password) VALUES (:uid, :pwd)",
            {"uid": user_id, "pwd": user_pwd})
            log="CREATED USER : User : "+user_id+" & Password : "+user_pwd
            db.commit()
            db.execute("INSERT INTO d_book.syslog (log_text) VALUES (:log)",
            {"log": log})
            db.commit()
            message="User "+user_id+" created"
            return render_template("auth.html" ,  message=message)

@app.route("/<isbn>" , methods=["POST" , "GET"])
def details(isbn):
    error=""
    message=""
    user = session['username']
    avg_rat=0.0
    but_act = request.form.get("but_act")
    rev_text = request.form.get("rev_text")
    rating= request.form.get("review_rating")
    if but_act=="Submit":
        if db.execute("SELECT * FROM d_book.reviews WHERE isbn=:isbn and user_id = :uid ", {"isbn": isbn , "uid": user}).rowcount != 0:
            error ="You have arelady reviewed this book"
            log="DUPLICATE REVIEW TRY: User : "+ user +" & isbn : "+isbn
            db.execute("INSERT INTO d_book.syslog (log_text) VALUES (:log)",
            {"log": log})
            db.commit()
        else:
            db.execute("INSERT INTO d_book.reviews (isbn, user_id , rating, text) VALUES (:isbn, :uid ,:rating, :text)",
            {"isbn": isbn, "uid": user, "rating": rating ,"text" :rev_text })
            db.commit()
            log="REVIEW CREATED : User : "+user+" for ISBN : "+isbn
            db.execute("INSERT INTO d_book.syslog (log_text) VALUES (:log)",
            {"log": log})
            db.commit()
            message="Review submitted successfully"


    book = db.execute("SELECT isbn,title,author, year FROM d_book.books WHERE isbn = :isbn ", {"isbn": isbn }).fetchone()
    if book is None:
        log="DETAIL INVAID ISBN : "+user+" & ISBN: "+isbn
        db.execute("INSERT INTO d_book.syslog (log_text) VALUES (:log)",
        {"log": log})
        db.commit()
        error ="Invalid ISBN"
        return render_template("index.html" , error=error)
    reviews=db.execute("SELECT user_id ,DATE(time_stamp) as date ,text , rating FROM d_book.reviews WHERE isbn = :isbn ", {"isbn": isbn }).fetchall()
    result=db.execute("SELECT avg(rating) as avg FROM d_book.reviews WHERE isbn = :isbn ", {"isbn": isbn }).fetchall()
    for i in result:
        if i[0] is not None:
            avg_rat= round(i[0] , 2)
    #Goodreads API call
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "rBd21ydiB25Cs6s9xErPiQ", "isbns": isbn})
    if res.status_code == 200:
        data=res.json()
        rev_no = data['books'][0]['work_ratings_count']
        gr_rat = data['books'][0]['average_rating']
    else:
        log="FAILED API CALL : "+user+" & ISBN: "+isbn
        db.execute("INSERT INTO d_book.syslog (log_text) VALUES (:log)",
        {"log": log})
        db.commit()
        rev_no ="N/A"
        gr_rat="N/A"

    return render_template("details.html" , book=book , reviews=reviews , avg_rat=avg_rat , gr_rat=gr_rat , user=user ,error=error ,message=message , rev_no=rev_no)

@app.route("/api/<isbn>")
def book_api(isbn):
    avg_rat=0.0
    rev_count=0
    book = db.execute("SELECT isbn,title,author, year FROM d_book.books WHERE isbn = :isbn ", {"isbn": isbn }).fetchone()
    if book is None:
        log="API REQUEST INVAID ISBN :" +isbn
        db.execute("INSERT INTO d_book.syslog (log_text) VALUES (:log)",
        {"log": log})
        db.commit()
        return jsonify({"error":"ISBN Not Found in our database"}), 404
    else:
        result=db.execute("SELECT avg(rating) as avg , count(*) as count FROM d_book.reviews WHERE isbn = :isbn ", {"isbn": isbn }).fetchall()
        for i in result:
            if i[0] is not None:
                avg_rat= round(i[0] , 2)
                rev_count=int(i[1])
        return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "review_count": avg_rat,
            "average_score": rev_count
            }) ,200
