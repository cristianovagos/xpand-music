from webproj.app.db.BaseXClient import Session

# create session
session = Session('localhost', 1984, 'admin', 'admin')

try:
    # create new database
    session.create("xpand-db", "<artists></artists>")
    print(session.info())

finally:
    # close session
    if session:
        session.close()