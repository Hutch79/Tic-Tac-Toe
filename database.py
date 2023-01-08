import mysql.connector

db = None


# =====================================================================================================================
# connectDB
# ----------------------------------------------------------------------------------------------------------------------
# Description:
#   Connects to a Database with given Login data
# ---------------------------------------------------------------------------------------------------------------------
# Return:
#   try: Database connection  # Successfully connected to Database
#   except: False  # Failed to connect to Database
# =====================================================================================================================
def connectDB():
    global db
    try:
        db = mysql.connector.connect(
            host="SQL.DOMAIN.EXAMPLE",
            user='SQL-USER',
            password="PASSWORD",
            database="SQL-DATABASE"
        )
        dbcursor = db.cursor()
        dbcursor.execute("CREATE TABLE IF NOT EXISTS userdata (id DECIMAL(30, 0), username VARCHAR(100), password "
                         "VARCHAR(100), win DECIMAL(30, 0), lost DECIMAL(30, 0), total_games DECIMAL(30, 0), "
                         "user_input DECIMAL(30, 0), enemy DECIMAL(30, 0))")
        print("MySQL Connected")
        return db
    except Exception:
        print("MySQL Connection Error")
        return False


# =====================================================================================================================
# getDBConnection
# ----------------------------------------------------------------------------------------------------------------------
# Description:
#   get Database connection
# ---------------------------------------------------------------------------------------------------------------------
# Return:
#   Database connection
# =====================================================================================================================
def getDBConnection():
    global db
    return db


# =====================================================================================================================
# isConnected
# ----------------------------------------------------------------------------------------------------------------------
# Description:
#   Check if Database is connected.
# ---------------------------------------------------------------------------------------------------------------------
# Return:
#   True: Connected
#   False: Not connected
# =====================================================================================================================
def isConnected():
    global db
    try:
        dbcursor = db.cursor()
        return True
    except Exception:
        return False


# =====================================================================================================================
# getUser
# ----------------------------------------------------------------------------------------------------------------------
# Description:
#   get userdata stored in the Database
# ---------------------------------------------------------------------------------------------------------------------
# Return:
#   Depending on argument `data`
#   Possible returns: username, password (hash), win, lost, total, enemy, user_input
# =====================================================================================================================
def getUser(userid, data):
    dbcursor = db.cursor()

    dbcursor.execute("select MAX(id) from userdata")  # Get highest userid
    maxID = dbcursor.fetchone()
    if userid > maxID[0]:  # Check if this UserID exists
        print(f"ERROR: Try to get non existent User - ID Provided: {userid} - MaxID: {maxID[0]}")  # Send Error-message
        return

    match data:
        case 'username':
            dbcursor.execute(f"SELECT username FROM userdata WHERE id = '{userid}'")  # Get username
            username = ''.join(dbcursor.fetchone())  # convert into string
            return username
            pass
        case 'password':
            dbcursor.execute(f"SELECT password FROM userdata WHERE id = '{userid}'")  # Get password
            password = ''.join(dbcursor.fetchone())  # convert into string
            return password
            pass
        case 'win':
            dbcursor.execute(f"SELECT win FROM userdata WHERE id = '{userid}'")  # Get wins
            win = dbcursor.fetchone()
            win = int(win[0])  # convert into int
            return win
            pass
        case 'lost':
            dbcursor.execute(f"SELECT lost FROM userdata WHERE id = '{userid}'")  # Get loses
            lost = dbcursor.fetchone()
            lost = int(lost[0])  # convert into int
            return lost
            pass
        case 'total':
            dbcursor.execute(f"SELECT total_games FROM userdata WHERE id = '{userid}'")  # Get total_games
            total = dbcursor.fetchone()
            total = int(total[0])  # convert into int
            return total
            pass
        case 'enemy':
            dbcursor.execute(f"SELECT enemy FROM userdata WHERE id = '{userid}'")  # Get enemy
            enemy = dbcursor.fetchone()
            enemy = int(enemy[0])  # convert into int
            return enemy
            pass
        case 'user_input':
            dbcursor.execute(f"SELECT user_input FROM userdata WHERE id = '{userid}'")  # Get enemy
            user_input = dbcursor.fetchone()
            user_input = int(user_input[0])  # convert into int
            return user_input
            pass
        case _:
            print(
                f"Error: Please define an correct datatype - Provided: {data} - Accepted: ['username', 'password', "
                f"'win', 'lost', 'total', 'enemy', 'user_input']")


# =====================================================================================================================
# updateUser
# ----------------------------------------------------------------------------------------------------------------------
# Description:
#   Reads all Userdata out of the Database and checks if something should be changed. If true, add changes to existing
#   value and write it back to Database.
# ---------------------------------------------------------------------------------------------------------------------
# Return:
#   -
# =====================================================================================================================
def updateUser(userid, username=None, password=None, win=0, lost=0, total=0, enemy=None, user_input=None):
    dbcursor = db.cursor()

    dbcursor.execute("select MAX(id) from userdata")  # Get highest userid
    maxID = dbcursor.fetchone()
    if userid > int(maxID[0]):  # Check if this UserID exists
        print(f"ERROR: Try to Edit non existent User - ID Provided: {userid} - MaxID: {maxID[0]}")  # Send Error-message
        return

    win_new = win + getUser(userid, 'win')  # Add existing data to new data
    lost_new = lost + getUser(userid, 'lost')
    total_new = total + getUser(userid, 'total')

    if enemy is None:
        enemy_new = getUser(userid, 'enemy')
    else:
        enemy_new = enemy

    if user_input is None:
        user_input_new = getUser(userid, 'user_input')
    else:
        user_input_new = user_input

    if username is None:  # Check if the Username got changed.
        username_new = getUser(userid, 'username')
    else:
        username_new = username

    if password is None:  # Check if the Password got changed.
        password_new = getUser(userid, 'password')
    else:
        import userManagement
        password_new = userManagement.createPassword(password)
        del userManagement
    dbcursor.execute(f"DELETE FROM userdata WHERE id = '{userid}'")  # Delete user to recreate it
    sql = "INSERT INTO `userdata` (`id`, `username`, `password`, `win`, `lost`, `total_games`, `user_input`, " \
          "`enemy`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"  # Prepare MySQL command
    val = (userid, username_new, password_new, win_new, lost_new, total_new, user_input_new,
           enemy_new)  # Prepare data to use in MySQL command
    dbcursor.execute(sql, val)  # Execute command
    db.commit()  # send command
    pass
