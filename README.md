# 📚 Personal Book Vault

Personal Book Vault is a Flask-based web application that allows users to maintain their own personal digital library.

Users can:

- Register and log in
- Add books to the system
- Upload book cover images
- Add books to their personal library
- Track reading progress
- Set reading status
- Rate books
- Add personal notes
- Organize books into collections
- View complete book details
- Update their book information
- Remove books from their library
- Search books in their library
- View library statistics

The project is built using Flask, Flask-SQLAlchemy, Flask-Login, Flask-Migrate, SQLite, Jinja2, HTML, CSS and JavaScript.

---

# 1. Project Objective

The main objective of Personal Book Vault is to create a simple book-management system where every user can maintain their own personal library.

Instead of storing only book information, the application separates:

1. General information about a book
2. User-specific information about that book

For example:

A book such as:

> Clean Code — Robert C. Martin

is a general book.

Different users can have the same book in their libraries but have different:

- Reading status
- Current page
- Rating
- Notes
- Collection
- Start date
- End date

Therefore, the application uses separate `Book` and `Userbook` models.

---

# 2. Main Features

## Authentication

Users can:

- Register
- Login
- Logout

Each user has:

- PID
- Email
- Username
- Password

Flask-Login is used to maintain the logged-in user's session.

---

## Book Management

Users can add books with:

- Title
- Author
- Language
- Genre
- Description
- Total pages
- Published year
- Cover image

The book is stored in the database.

---

## Personal Library

After adding a book, the user can add it to their personal library.

The user can specify:

- Status
- Current page
- Collection
- Rating
- Personal note
- Start date
- End date

---

## Reading Status

Books can have different statuses such as:

- To Read
- Reading
- Completed

The status helps users track their reading progress.

---

## Reading Progress

The application stores the current page of the book.

For example:

```text
250 / 450
