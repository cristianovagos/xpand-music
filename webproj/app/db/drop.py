from webproj.app.db.BaseXClient import Session

# create session
session = Session('localhost', 1984, 'admin', 'admin')

try:
    # drop the database
    session.execute("drop db xpand-db")

finally:
    # close session
    if session:
        session.close()