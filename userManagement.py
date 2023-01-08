import bcrypt
import re

from database import getDBConnection


# =====================================================================================================================
# createPassword
# ----------------------------------------------------------------------------------------------------------------------
# Description:
#   Hashes a given Password and returns it.
# ---------------------------------------------------------------------------------------------------------------------
# Return:
#   Password Hash
# =====================================================================================================================
def createPassword(password):
    # Hashing the password
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


# =====================================================================================================================
# checkPassword
# ----------------------------------------------------------------------------------------------------------------------
# Description:
#   Checks a given password with a given Hash.
# ---------------------------------------------------------------------------------------------------------------------
# Return's:
#   True: Password and Hash match
#   False: Password and Hash did not match
# =====================================================================================================================
def checkPassword(password, hashed):
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# =====================================================================================================================
# Login
# ----------------------------------------------------------------------------------------------------------------------
# Description:
#   Checks if the given Username exists. If true it checks the given Password with the Password Hash in the Database.
# ---------------------------------------------------------------------------------------------------------------------
# Return's:
#   userid: Logged in
#   False: Wrong password or Username
#   -2: Illegal characters in username
# =====================================================================================================================
def login(username, password):
    if username == '':
        return False
    else:
        existingUsername_var = existingUsername(username)  # Variable to optimize performance
        if existingUsername_var is True:
            dbcursor = getDBConnection().cursor()
            dbcursor.execute(f"SELECT password FROM userdata WHERE username = '{username}'")  # Get password
            user = dbcursor.fetchone()
            if checkPassword(password, ''.join(user)):  # check if password is correct
                dbcursor.execute(f"SELECT id FROM userdata WHERE username = '{username}'")  # Get username
                userid = dbcursor.fetchone()
                userid = int(userid[0])
                print("You are logged in as " + username)
                return userid
            else:
                return False
        elif existingUsername_var is False:
            return False
        elif existingUsername_var == -2:
            return -2


# =====================================================================================================================
# Signup
# ---------------------------------------------------------------------------------------------------------------------
# Description:
#   Checks if the given Username already exists, if not it creates a new User with the give Username and Password as
#   well as creating a new UserID
# ---------------------------------------------------------------------------------------------------------------------
# Return's:
#   UserID: User was Created successfully
#   True: Username already exists
#   -2: Illegal characters in username
# =====================================================================================================================
def signup(username, password):
    dbcursor = getDBConnection().cursor()

    signup_var = existingUsername(username)

    if signup_var is False:
        dbcursor.execute("select MAX(id) from userdata")  # Get highest userid
        maxID = dbcursor.fetchone()  # save the highest user id in maxID
        if maxID[0] is None:  # check if maxID is Null if true set to 1
            maxID_new = 1
        else:
            maxID_new = int(maxID[0]) + 1  # Increment ID to get an unused ID
            pass

        sql = "INSERT INTO `userdata` (`id`, `username`, `password`, `win`, `lost`, `total_games`, `user_input`, " \
              "`enemy`) VALUES (%s, %s, %s, 0, 0, 0, 0, 0)"  # Prepare MySQL command
        val = (maxID_new, username, createPassword(password))  # Prepare data to use in MySQL command
        dbcursor.execute(sql, val)  # Execute command
        getDBConnection().commit()  # send command
        return maxID_new
    else:
        return signup_var
    pass


# =====================================================================================================================
# existingUsername
# ---------------------------------------------------------------------------------------------------------------------
# Description:
#   Checks if the given Username already exists in the Database and meats the regex expression (Letters Numbers . _ -).
#   Case insensitive!
# ---------------------------------------------------------------------------------------------------------------------
# Returns:
#   True: Username exist
#   False: Username does not exist
#   -2: Illegal character in Username (Does not match with Regex)
# =====================================================================================================================
def existingUsername(user):  # If username exists return True if not return False.
    pattern = re.compile("([A-Za-z0-9._-]+)")  # Before testing check against Regex. If no match return False.
    if pattern.fullmatch(user):
        dbcursor = getDBConnection().cursor()
        dbcursor.execute("select username from userdata")  # Get all usernames from Database
        hui2 = dbcursor.fetchall()
        username = [row[0] for row in hui2]  # Store Usernames in username and convert them to string list
        usernameConverted = [x.upper() for x in username]  # convert all strings in list to upper
        if usernameConverted.count(user.upper()):  # check if input is in string list
            return True
        else:
            return False
    else:
        return -2
    pass
