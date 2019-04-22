import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
#with engine.connect() as conn:
#            conn.execute('SET search_path TO d_book')
db = scoped_session(sessionmaker(bind=engine))

def main():
    file= open("books.csv")
    read_dta = csv.reader(file)
    for isbn, title, author, year in read_dta:
        log_text ="";
        if db.execute("SELECT * FROM d_book.books WHERE isbn = :isbn", {"isbn": isbn}).rowcount == 0:
            db.execute("INSERT INTO d_book.books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
            log_text = f"Added book number {isbn} titled {title} written by {author} in year {year}."
            db.execute("INSERT INTO d_book.syslog (log_text) VALUES (:log_text)",
                    {"log_text": log_text})
        else:
            log_text = f"ALREADY EXISTS Book number {isbn} titled {title} written by {author} in year {year}."
            db.execute("INSERT INTO d_book.syslog (log_text) VALUES (:log_text)",
                    {"log_text": log_text})
    db.commit()

if __name__ == "__main__":
    main()
