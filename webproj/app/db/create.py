from .BaseXClient import Session

def createDatabase():
    # create session
    print("Initializing session...")
    session = Session('localhost', 1984, 'admin', 'admin')

    try:
        # create new database
        print("Creating a new database...")
        session.create("xpand-db", "<artists></artists>")

    except Exception as e:
        print("Oops, something has failed!")
        print("Exception: " + str(e))

    finally:
        # close session
        if session:
            session.close()