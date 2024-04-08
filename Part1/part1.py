import smtplib
import pyautogui as py #Import pyautogui
import json
import sys

# Helper function to send email when entering box 
def send_email_enter(sender, receiver, msg):
    try:
        server.sendmail(sender_email, receiver_email, msg)
        print("\nCursor entered the box, email sent successfully.")
    except smtplib.SMTPException as e:
        print.error(f"Error sending email: {e}")

# Helper function to send email when exiting box
def send_email_exit(sender, receiver, msg):
    try:
        server.sendmail(sender_email, receiver_email, msg)
        print("\nCursor exited box, email sent successfully.")
    except smtplib.SMTPException as e:
        print.error(f"Error sending email: {e}")
    
    
    
with open('Part1\data.json') as f:
    data = json.load(f)

# Get the data from the json file
x1 = data["rect"]["x1"]
y1 = data["rect"]["y1"]
x2 = data["rect"]["x2"] 
y2 = data["rect"]["y2"]
sender_email = data["email"]["sender"]
password = data["email"]["password"]
receiver_email = data["email"]["receiver"]

# Messages to be sent in the email
enter_msg = 'Cursor entered the rect.'
exit_msg = 'Cursor left the rect.'

# Initialize the flag
isInside = False

# SMTP server details
PORT = 587
HOST = "smtp.gmail.com"

try:
    # Smtp handling
    server = smtplib.SMTP(HOST, PORT)
    server.starttls()
    server.login(sender_email,password)

    # Main loop
    while True: # Start loop
        x , y = py.position()
        if ( (isInside==False) and (x2>x>x1 and y2>y>y1)):  #if we are inside the rect, send once
            isInside = True
            send_email_enter(sender_email,receiver_email,enter_msg)
        elif ((isInside==True) and (not (x2>x>x1 and y2>y>y1))):  # if we are outside the rect, send once
            isInside = False
            send_email_exit(sender_email,receiver_email,exit_msg)
        else:
            print("\rCoordinates: X={}, Y={}".format(x, y), end="")
            sys.stdout.flush()
except KeyboardInterrupt:
    print("\nProgram terminated by user.")
except Exception as e:
    print(f"Received an error: {e}")
finally:
    server.quit()
