# Project 1

Web Programming with Python and JavaScript

Submission for the CS50 Webcourse Project 1 Assignment.

D Book is a book review portal where you could search for your fav. books and review and rate them. The site also fetches average rating from the site goodreads.com for comparison.

API:
  The details of a book could also be request via an API call as shown below:

  <"web url">/api/<isbn>  where "web url" is the url where this would be hosted <isbn> is an ISBN number.
  
  A sample call and returned value.
  
    http://127.0.0.1:5000/api/006093140X
    {"author":"Doris Lessing","average_score":0,"isbn":"006093140X","review_count":0.0,"title":"The Golden Notebook","year":"1962"}
  
  In case no record found with the isbn it returns a 404 code along with the below json.Example:
  
    http://127.0.0.1:5000/api/006040X
    {"error":"ISBN Not Found in our database"}
     
Below listed are the file names and a short description explaining their purpose.

*Files:Descriptions

1. static/D_Book.png : Logo for the site header.
2. static/no_image.jpg : Display pic for each book on the detail page.
3. static/styles.css : Style sheet of the site.
4. templates/layout.html : Site Layout template.
5. templates/index.html : main page with search and listing of books.
6. templates/auth.html : login and sign up page.
7. templates/details.html :details of the selected book and list of its reviews.
8. /application.py: main python program populating the site with data.
9. /import.py : import the books provided in books.csv to the site database.

DataBase:

The database used is Postgres and the shema name should be d_book

There are 4 tables(column names with indentation)

books
  isbn(PK)
  title
  author
  year
  time_stamp
  
reviews
  isbn(PK)
  user_id(PK)
  rating
  text
  time_stamp
  
user
  user_id(PK)
  password
  time_stamp

  
