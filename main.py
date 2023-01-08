import struct
import random
from guizero import *
from time import sleep

import serial
import serial.tools.list_ports

# Get a list of all available serial ports
ports = list(serial.tools.list_ports.comports())

ser = None

# Iterate over the list of ports and try to find the correct one
for port in ports:
    # Check if the port is the one we want
    if "SER" in port.description.upper():
        # Open the serial port
        ser = serial.Serial(port.device, 9600)
        break


def skip():
    Gamemode_selector.show()
    ErrorApp.hide()


def enter():
    global ser
    try:
        ser = serial.Serial(TB1.value, 9600)
        print(ser.port)
        print("Success")
        connections()
        Gamemode_selector.show()
        ErrorApp.hide()
    except:
        print("Error")


if ser is None:
    ErrorApp = App(title="Serial Error")
    T1 = Text(ErrorApp, text="Please enter your Port manually!")
    TB1 = TextBox(ErrorApp)
    PB1 = PushButton(ErrorApp, command=skip, text="Skip Port")
    PB2 = PushButton(ErrorApp, command=enter, text="Set Port")

# =====================================================================================================================
# Self created Imports
# =====================================================================================================================
import database
import userManagement

db = database.connectDB()  # Creating database connection

# =====================================================================================================================
# Global variables
# =====================================================================================================================
how = 1  # Which player is currently clicking
player1_id = None  # ID of player 1
player1_name = None  # Name of player 1
player1_key = []  # Clicked buttons of player 1
player2_id = None  # ID of player 2
player2_name = None  # Name of player 2
player2_key = []  # Clicked buttons of player 2
pushed_count = 0  # How many buttons where pushed
reset_request_count = 0  # How many resets were requested
# ToDo: Rewrite reset system to check UserID's. maybe use player_key variables?
remote_user = 0  # Userid of remote user
gamemode = None
how_am_i = None


# =====================================================================================================================
# gameSwitch
# ---------------------------------------------------------------------------------------------------------------------
# Disables all game-buttons and enables them again
# =====================================================================================================================
def gameSwitch(status):
    global player2_key, player1_key
    if status == 0:
        Bgame.disable()
    if status == 1:
        Bgame.enable()
        if '1' in player1_key or '1' in player2_key:
            P1.disable()
        if '2' in player1_key or '2' in player2_key:
            P2.disable()
        if '3' in player1_key or '3' in player2_key:
            P3.disable()
        if '4' in player1_key or '4' in player2_key:
            P4.disable()
        if '5' in player1_key or '5' in player2_key:
            P5.disable()
        if '6' in player1_key or '6' in player2_key:
            P6.disable()
        if '7' in player1_key or '7' in player2_key:
            P7.disable()
        if '8' in player1_key or '8' in player2_key:
            P8.disable()
        if '9' in player1_key or '9' in player2_key:
            P9.disable()


def push(key_val):
    global how, player1_key, player2_key, pushed_count, reset_request_count, gamemode

    print(f"how: {how}/{how_am_i} - Key: {key_val} - type: {type(key_val)}")

    if type(key_val) == int:
        key = str(key_val)
    else:
        key = key_val

    match key:  # Deactivate used Buttons and chance value
        case '1':
            print("huiiiiiiiiiiiii")
            P1.disable()
            if how == 2:
                P1.text = 'O'
            else:
                P1.text = 'X'
                print("huiiiiiiiiiiiii2")
            pushed_count = pushed_count + 1
        case '2':
            P2.disable()
            if how == 2:
                P2.text = 'O'
            else:
                P2.text = 'X'
            pushed_count = pushed_count + 1
        case '3':
            P3.disable()
            if how == 2:
                P3.text = 'O'
            else:
                P3.text = 'X'
            pushed_count = pushed_count + 1
        case '4':
            P4.disable()
            if how == 2:
                P4.text = 'O'
            else:
                P4.text = 'X'
            pushed_count = pushed_count + 1
        case '5':
            P5.disable()
            if how == 2:
                P5.text = 'O'
            else:
                P5.text = 'X'
            pushed_count = pushed_count + 1
        case '6':
            P6.disable()
            if how == 2:
                P6.text = 'O'
            else:
                P6.text = 'X'
            pushed_count = pushed_count + 1
        case '7':
            P7.disable()
            if how == 2:
                P7.text = 'O'
            else:
                P7.text = 'X'
            pushed_count = pushed_count + 1
        case '8':
            P8.disable()
            if how == 2:
                P8.text = 'O'
            else:
                P8.text = 'X'
            pushed_count = pushed_count + 1
        case '9':
            P9.disable()
            if how == 2:
                P9.text = 'O'
            else:
                P9.text = 'X'
            pushed_count = pushed_count + 1
    reset_request_count = 0

    if how == 1:  # Add pushed button to Player 1 or 2
        player1_key.append(key)
        check_winner()
    else:
        player2_key.append(key)
        check_winner()

    if gamemode == 3:
        if how != how_am_i: # My Turn over
            ser.write(struct.pack('<H', int(key)))
            # gameSwitch(0)
            gm3_check_enemy()
        elif how == how_am_i:
            # gameSwitch(1)
            pass
    pass


# =====================================================================================================================
# check_winner
# ---------------------------------------------------------------------------------------------------------------------
# Checks if a User has 3 in a row.
# =====================================================================================================================
def check_winner():
    global how, player1_id, player2_id, pushed_count, player2_key, player1_key, gamemode
    options = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9'], ['1', '4', '7'], ['2', '5', '8'], ['3', '6', '9'],
               ['1', '5', '9'], ['3', '5', '7']]  # Win options

    if how == 1:
        how = 2
        T1.value = f"{player2_name}'s turn"
        x = 0
        while x < 8:  # Check if Player1 has won
            if all(x in player1_key for x in options[x]):
                print("Player 1 has won!")
                if gamemode == 3:
                    ser.write(struct.pack('<H', 11))
                if db is not False and type(db) != bool:
                    database.updateUser(player1_id, win=1, total=1)
                    database.updateUser(player2_id, lost=1, total=1)
                reset_game()
            x = x + 1
    elif how == 2:
        how = 1
        T1.value = f"{player1_name}'s turn"
        y = 0
        while y < 8:  # Check if Player2 has won
            if all(y in player2_key for y in options[y]):
                print("Player 2 has won!")
                if gamemode == 3:
                    ser.write(struct.pack('<H', 12))
                if db is not False and type(db) != bool:
                    database.updateUser(player1_id, lost=1, total=1)
                    database.updateUser(player2_id, win=1, total=1)
                reset_game()
            y = y + 1

    if pushed_count >= 9:
        print("No Winner")
        if gamemode == 3:
            ser.write(struct.pack('<H', 10))
        if db is not False and type(db) != bool:
            database.updateUser(player1_id, total=1)
            database.updateUser(player2_id, total=1)
        reset_game()
    pass


def reset_request():  # ToDo: Recode
    global reset_request_count
    if reset_request_count >= 1:
        reset_game()
    else:
        reset_request_count = reset_request_count + 1


# =====================================================================================================================
# reset_game
# ---------------------------------------------------------------------------------------------------------------------
# Resets the GUI and Variables to standard values at Gamestart
# =====================================================================================================================
def reset_game():
    global player1_id, player2_id, pushed_count, reset_request_count, how, player1_key, player2_key
    P1.enable()
    P2.enable()
    P3.enable()
    P4.enable()
    P5.enable()
    P6.enable()
    P7.enable()
    P8.enable()
    P9.enable()
    P1.text = '1'
    P2.text = '2'
    P3.text = '3'
    P4.text = '4'
    P5.text = '5'
    P6.text = '6'
    P7.text = '7'
    P8.text = '8'
    P9.text = '9'
    player1_key.clear()
    player2_key.clear()
    pushed_count = 0
    reset_request_count = 0
    how = 1
    T1.value = f"{player1_name}'s turn"
    pass


# _gms2
def hui():  # Empty placeholder function to satisfy empty buttons
    print("Huiiii im a empty function")
    pass


# =====================================================================================================================
# App
# ---------------------------------------------------------------------------------------------------------------------
# App Section
# =====================================================================================================================
app = App(title="Tic-Tac-Toe")
app.hide()

huii = 0


def huiii():
    global huii
    if huii == 1:
        huii = 0
        gameSwitch(0)
    elif huii == 0:
        huii = 1
        gameSwitch(1)


Bmain = Box(app, layout='grid')
T1 = Text(app, text="Player 1's turn")
T2 = Text(app, text='')
Bgame = Box(Bmain, layout='grid', border=True, grid=[0, 0])
P1 = PushButton(Bgame, command=push, args='1', text='1', grid=[0, 0], width=2, height=2)
P2 = PushButton(Bgame, command=push, args='2', text='2', grid=[1, 0], width=2, height=2)
P3 = PushButton(Bgame, command=push, args='3', text='3', grid=[2, 0], width=2, height=2)
P4 = PushButton(Bgame, command=push, args='4', text='4', grid=[0, 1], width=2, height=2)
P5 = PushButton(Bgame, command=push, args='5', text='5', grid=[1, 1], width=2, height=2)
P6 = PushButton(Bgame, command=push, args='6', text='6', grid=[2, 1], width=2, height=2)
P7 = PushButton(Bgame, command=push, args='7', text='7', grid=[0, 2], width=2, height=2)
P8 = PushButton(Bgame, command=push, args='8', text='8', grid=[1, 2], width=2, height=2)
P9 = PushButton(Bgame, command=push, args='9', text='9', grid=[2, 2], width=2, height=2)
P10 = PushButton(Bmain, command=reset_request, text='Reset', grid=[0, 3, 3, 3])


# =====================================================================================================================
# MeuBar
# ---------------------------------------------------------------------------------------------------------------------
# MenuBar Section
# =====================================================================================================================
def settings_buttons():  # MenuBar
    settings.show()


def about_buttons():  # MenuBar
    about.show()


menubar = MenuBar(app,
                  toplevel=["Options"],
                  options=[
                      [["Settings", settings_buttons], ["About", about_buttons]]
                  ])

# =====================================================================================================================
# Settings
# ---------------------------------------------------------------------------------------------------------------------
# Settings Section
# =====================================================================================================================
settings = Window(app, title="Settings")
choose_player = ButtonGroup(settings, options=["player1", "player2"], horizontal='True')
change_name = PushButton(settings, text="Change Name")
change_password = PushButton(settings, text="Change Password")
settings.hide()

# change_password_player1 = Window(change_password, title="Change Password Player1")
# change_password_player1.hide()
#
# change_password_player2 = Window(change_password, title="Change Password Player2")
# change_password_player2.hide()
#
# change_name_player1 = Window(change_name, title="Change Name Player1")
# change_name_player1.hide()
#
# change_name_player1 = Window(change_name, title="Change Name Player1")
# change_name_player1.hide()

# =====================================================================================================================
# About
# ---------------------------------------------------------------------------------------------------------------------
# About Section
# =====================================================================================================================
about = Window(app, title="About")
t_box1 = TextBox(about, width='fill', height='5', multiline='True',
                 text='Thank you for playing our game.\nFeedback is always appreciated!', enabled=False)
t_box2 = TextBox(about, width='fill', height='fill', multiline='True', text='Creaters:\nAndrin Monn\nRaphael Lanza',
                 enabled=False)
about.hide()


# =====================================================================================================================
# Gamemode Selector
# ---------------------------------------------------------------------------------------------------------------------
# Gamemode Selector Section
# =====================================================================================================================

def gms0():
    global gamemode
    gamemode = 0
    global db
    db = False
    app.show()
    app.title = "Tic Tac Toe - Offline Mode"
    Gamemode_selector.hide()


def gms1():
    global gamemode
    gamemode = 1
    gm1_login.show()
    Gamemode_selector.hide()


def gms2():
    global gamemode
    gamemode = 2
    ser.write(struct.pack('<H', 1))
    wait.show()
    print(int(struct.unpack('<H', ser.read(2))[0]))
    ser.write(struct.pack('<H', 1))
    wait.hide()
    gm2_login.show()
    Gamemode_selector.hide()

    pass


def gms3():
    global gamemode, how_am_i, db
    gamemode = 3
    # value = random.randint(100, 65535)
    value = 101
    ser.write(struct.pack('<H', value))
    wait.show()
    rx = int(struct.unpack('<H', ser.read(2))[0])
    ser.write(struct.pack('<H', value))
    if rx > value:
        how_am_i = 2
        gm3_check_enemy()
    else:
        how_am_i = 1
    print(f"how_am_i: {how_am_i}")
    wait.hide()
    app.show()
    Gamemode_selector.hide()
    db = False
    pass


wait = Window(app, title="Waiting")
wait.hide()
Twait = Text(wait, text="Waiting fot the other Player. Pleas be patient.")

Gamemode_selector = Window(app, title='Gamemode Selector')
if ser is None:
    Gamemode_selector.hide()
gmPB1 = PushButton(Gamemode_selector, command=gms1, text='Single Device - Online', enabled=True)
gmPB0 = PushButton(Gamemode_selector, command=gms0, text='Single Device - Offline', enabled=True)
gmPB2 = PushButton(Gamemode_selector, command=gms2, text='Multi Device - Online', enabled=True)
gmPB3 = PushButton(Gamemode_selector, command=gms3, text='Multi Device - Offline', enabled=True)


def connections():
    gmPB0.enable()
    gmPB1.enable()
    gmPB2.enable()
    gmPB3.enable()
    if ser is None:
        gmPB2.disable()
        gmPB3.disable()
        if db is False and type(db) == bool:
            gmPB1.disable()
            app.info(title='Warning!', text='Now were in Trouble! No Database connection and no Serial connection. Its '
                                            'simple to choose now ^^')
            return
        app.info(title='Warning!', text='We were unable to connect to the Serial port.')

    if db is False and type(db) == bool:
        gmPB1.disable()
        gmPB2.disable()
        if ser is None:
            gmPB3.disable()
            app.info(title='Warning!', text='Now were in Trouble! No Database connection and no Serial connection. Its '
                                            'simple to choose now ^^')
            return
        app.info(title='Warning!', text='We were unable to connect to the Database.')


connections()

# =====================================================================================================================
# Gamemode 1 Login
# ---------------------------------------------------------------------------------------------------------------------
# Multiplayer one devices
# =====================================================================================================================
gm1_login = Window(app, title='Login')
gm1_login.hide()


def fgm1_login(nr):
    global player1_id, player2_id, player1_name, player2_name

    if nr == "1":
        user = gm1_u1TB1.value
        password = gm1_u1TB2.value
    else:
        user = gm1_u2TB1.value
        password = gm1_u2TB2.value

    login_var = userManagement.login(user, password)

    if login_var > 0 and type(login_var) == int:  # Login Successfully
        if nr == "1":
            gm1_u1T1.value = f"You are logged in as {user}"
            player1_name = user
            player1_id = login_var
            gm1_u1TBox.disable()
        else:
            gm1_u2T1.value = f"You are logged in as {user}"
            player2_name = user
            player2_id = login_var
            gm1_u2TBox.disable()

    elif login_var is False and type(login_var) == bool:  # Login failed
        if nr == "1":
            gm1_u1T1.value = "Please check your Username or Password"
        else:
            gm1_u2T1.value = "Please check your Username or Password"

    elif login_var == -2 and type(login_var) == int:  # Username contains illegal characters
        if nr == "1":
            gm1_u1T1.value = "Illegal character in Username"
        else:
            gm1_u2T1.value = "Illegal character in Username"

    if player1_id is not None and player2_id is not None:
        app.show()
        app.title = "Tic Tac Toe - Online mode, Single device"
        gm1_login.hide()


def fgm1_signup(nr):
    global player1_id, player2_id, player1_name, player2_name

    if nr == "1":
        user = gm1_u1TB1.value
        password = gm1_u1TB2.value
    else:
        user = gm1_u2TB1.value
        password = gm1_u2TB2.value

    signup_var = userManagement.signup(username=user, password=password)

    if signup_var > 0 and type(signup_var) == int:  # Login Successfully
        if nr == "1":
            gm1_u1T1.value = f"You have signed up as {user}"
            player1_name = user
            player1_id = signup_var
            gm1_u1TBox.disable()
        else:
            gm1_u2T1.value = f"You have signed up as {user}"
            player2_name = user
            player2_id = signup_var
            gm1_u2TBox.disable()

    elif signup_var is True and type(signup_var) == bool:  # Username taken
        if nr == "1":
            gm1_u1T1.value = "Your Username is already taken"
        else:
            gm1_u2T1.value = "Your Username is already taken"

    elif signup_var == -2 and type(signup_var) == int:  # Username contains illegal characters
        if nr == "1":
            gm1_u1T1.value = "Illegal character in Username"
        else:
            gm1_u2T1.value = "Illegal character in Username"

    if player1_id is not None and player2_id is not None:
        app.show()
        app.title = "Tic Tac Toe - Online mode, Single device"
        gm1_login.hide()


# --------------------------
# Login User 1
# --------------------------
gm1_u1TBox = TitleBox(gm1_login, layout='grid', text='User 1 - Login')
gm1_u1T1 = Text(gm1_u1TBox, text='Please enter Login-data', grid=[1, 0, 2, 1])
gm1_u1B1 = Box(gm1_u1TBox, grid=[1, 1])
gm1_u1B2 = Box(gm1_u1TBox, grid=[2, 1])
gm1_u1T2 = Text(gm1_u1B1, text='Username:')
gm1_u1TB1 = TextBox(gm1_u1B2, text='', width=30)
gm1_u1T3 = Text(gm1_u1B1, text='Password:')
gm1_u1TB2 = TextBox(gm1_u1B2, text='', width=30, hide_text=True)
gm1_u1B3 = Box(gm1_u1TBox, grid=[1, 2])

gm1_u1PB1 = PushButton(gm1_u1B3, command=fgm1_login, args="1", align='left', text='Login')
gm1_u1PB1.text_color = 'black'
gm1_u1PB2 = PushButton(gm1_u1B3, command=fgm1_signup, args="1", align='right', text='Signup')
gm1_u1PB2.text_color = 'black'
# --------------------------
# Login User 1 end
# --------------------------


# --------------------------
# Login User 2
# --------------------------
gm1_u2TBox = TitleBox(gm1_login, layout='grid', text='User 2 - Login')
gm1_u2T1 = Text(gm1_u2TBox, text='Please enter Login-data', grid=[1, 0, 2, 1])
gm1_u2B1 = Box(gm1_u2TBox, grid=[1, 1])
gm1_u2B2 = Box(gm1_u2TBox, grid=[2, 1])
gm1_u2T2 = Text(gm1_u2B1, text='Username:')
gm1_u2TB1 = TextBox(gm1_u2B2, text='', width=30)
gm1_u2T3 = Text(gm1_u2B1, text='Password:')
gm1_u2TB2 = TextBox(gm1_u2B2, text='', width=30, hide_text=True)
gm1_u2B3 = Box(gm1_u2TBox, grid=[1, 2])

gm1_u2PB1 = PushButton(gm1_u2B3, command=fgm1_login, args="2", align='left', text='Login')
gm1_u2PB1.text_color = 'black'
gm1_u2PB2 = PushButton(gm1_u2B3, command=fgm1_signup, args="2", align='right', text='Signup')
gm1_u2PB2.text_color = 'black'
# --------------------------
# Login User 2 end
# --------------------------


# =====================================================================================================================
# Gamemode 2 Login
# ---------------------------------------------------------------------------------------------------------------------
# Multiplayer two devices no serial connection
# =====================================================================================================================
gm2_login = Window(app, title='Login')
gm2_login.hide()


def fgm2_login():
    global player1_id, player2_id, player1_name, player2_name

    user = gm2_u1TB1.value
    password = gm2_u1TB2.value

    login_var = userManagement.login(user, password)

    if login_var > 0 and type(login_var) == int:  # Login Successfully
        gm2_u1T1.value = f"You are logged in as {user} - UserID: {login_var}"
        player1_name = user
        player1_id = login_var
        gm2_u1TBox.disable()
        gm2_u2TBox.enable()

    elif login_var is False and type(login_var) == bool:  # Login failed
        gm2_u1T1.value = "Please check your Username or Password"

    elif login_var == -2 and type(login_var) == int:  # Username contains illegal characters
        gm2_u1T1.value = "Illegal character in Username"

    if player1_id is not None and player2_id is not None:
        app.show()
        app.title = "Tic Tac Toe - Online mode, Single device"
        gm1_login.hide()


def fgm2_signup():
    global player1_id, player2_id, player1_name

    user = gm2_u1TB1.value
    password = gm2_u1TB2.value

    signup_var = userManagement.signup(username=user, password=password)

    if signup_var > 0 and type(signup_var) == int:  # Login Successfully
        gm2_u1T1.value = f"You have signed up as {user} - UserID: {signup_var}"
        player1_name = user
        player1_id = signup_var
        gm2_u1TBox.disable()
        gm2_u2TBox.enable()

    elif signup_var is True and type(signup_var) == bool:  # Username taken
        gm2_u1T1.value = "Your Username is already taken"

    elif signup_var == -2 and type(signup_var) == int:  # Username contains illegal characters
        gm2_u1T1.value = "Illegal character in Username"

    if player1_id is not None and player2_id is not None:
        app.show()
        app.title = "Tic Tac Toe - Online mode, Single device"
        gm1_login.hide()


def gm2_setID():
    global remote_user, player1_id, player2_id, player2_name, player1_name, how_am_i
    dbcursor = db.cursor()
    dbcursor.execute("select MAX(id) from userdata")  # Get highest userid
    maxID = dbcursor.fetchone()
    maxID = int(maxID[0])

    if gm2_u2TB.value != '':
        if int(gm2_u2TB.value) <= maxID:
            if int(gm2_u2TB.value) != player1_id:
                remote_user = int(gm2_u2TB.value)
                database.updateUser(player1_id, enemy=remote_user)
                count = 0
                while count != 12:
                    count = count + 1
                    gm2_u2T0.value = f"Trying to connect to second user - {count} of 12 try's"
                    app.update()
                    print(f"Count: {count}")
                    enemy = database.getUser(remote_user, 'enemy')
                    if enemy == player1_id:
                        gm2_login.hide()
                        app.show()
                        player2_id = int(gm2_u2TB.value)
                        player2_name = database.getUser(player2_id, 'username')
                        gm2_u2T0.value = 'Set userID Successfully'
                        how_am_i = 1
                        if player2_id < player1_id:
                            how_am_i = 2
                            temp_id = player1_id
                            temp_name = player1_name
                            player1_id = player2_id
                            player1_name = player2_name
                            player2_id = temp_id
                            player2_name = temp_name
                        print(f"p1: {player1_name} - p2: {player2_name} - how_am_i: {how_am_i}")
                        if how_am_i == 2:
                            gameSwitch(0)
                            gm2_check_enemy()
                        else:
                            gameSwitch(1)
                        break
                    sleep(5)
            else:
                gm2_u2T0.value = "You can't play with yourself"
        else:
            gm2_u2T0.value = 'Please enter a valid UserID'
    else:
        gm2_u2T0.value = 'Please enter a valid UserID'
    gm2_u2T0.value = "Can't connect to second User"


# --------------------------
# Login User 1
# --------------------------
gm2_u1TBox = TitleBox(gm2_login, layout='grid', text='User 1 - Login')
gm2_u1T1 = Text(gm2_u1TBox, text='Please enter Login-data', grid=[1, 0, 2, 1])
gm2_u1B1 = Box(gm2_u1TBox, grid=[1, 1])
gm2_u1B2 = Box(gm2_u1TBox, grid=[2, 1])
gm2_u1T2 = Text(gm2_u1B1, text='Username:')
gm2_u1TB1 = TextBox(gm2_u1B2, text='', width=30)
gm2_u1T3 = Text(gm2_u1B1, text='Password:')
gm2_u1TB2 = TextBox(gm2_u1B2, text='', width=30, hide_text=True)
gm2_u1B3 = Box(gm2_u1TBox, grid=[1, 2])

gm2_u1PB1 = PushButton(gm2_u1B3, command=fgm2_login, align='left', text='Login')
gm2_u1PB1.text_color = 'black'
gm2_u1PB2 = PushButton(gm2_u1B3, command=fgm2_signup, align='right', text='Signup')
gm2_u1PB2.text_color = 'black'
# --------------------------
# Login User1 end
# --------------------------

# --------------------------
# Input Remote user
# --------------------------
gm2_u2TBox = TitleBox(gm2_login, text='Second user ID', layout='grid', enabled=False)
gm2_u2T0 = Text(gm2_u2TBox, text='', grid=[0, 0, 2, 1])
gm2_u2T1 = Text(gm2_u2TBox, text='Provide ID of second User', grid=[0, 1])
gm2_u2TB = TextBox(gm2_u2TBox, grid=[1, 1])
gm2_u2PB = PushButton(gm2_u2TBox, command=gm2_setID, grid=[0, 2, 2, 3])
gm2_u2PB.text_color = 'black'


# --------------------------
# Input Remote user end
# --------------------------

# =====================================================================================================================
# Gamemode 2
# ---------------------------------------------------------------------------------------------------------------------
# Stuff to run in gm2
# =====================================================================================================================
def gm2_check_enemy():
    global player2_key, player2_id, gamemode, how
    if how_am_i == 1:
        while True:
            print("player 2")
            user_input = database.getUser(player2_id, 'user_input')
            print(f"enemy input: {user_input}")
            if user_input != 0:
                player2_key.append(user_input)
                database.updateUser(player2_id, user_input=0)
                how = 1
                gameSwitch(1)
            print(f"enemy input: {user_input}")
            sleep(5)
    elif how_am_i == 2:
        while True:
            print("player 1")
            user_input = database.getUser(player1_id, 'user_input')
            print(f"enemy input: {user_input}")
            if user_input != 0:
                player1_key.append(user_input)
                database.updateUser(player1_id, user_input=0)
                how = 2
                gameSwitch(1)
            print(f"enemy input: {user_input}")
            sleep(5)


# =====================================================================================================================
# Gamemode 3
# ---------------------------------------------------------------------------------------------------------------------
# Stuff to run in gm3
# =====================================================================================================================
def gm3_check_enemy():
    print("Please execute")
    sleep(0.5)
    rx = int(struct.unpack('<H', ser.read(2))[0])
    if rx > 100:
        print(f"rx to high {rx}")
        rx = int(struct.unpack('<H', ser.read(2))[0])
    print(f"RX: {rx}")
    if rx <= 9:
        push(rx)
    elif rx == 11:
        print("Player 1 has won")
        reset_game()
        pass
    elif rx == 12:
        print("Player 2 has won")
        reset_game()
        pass
    elif rx == 10:
        print("No Winner")
        reset_game()
        pass

app.display()
