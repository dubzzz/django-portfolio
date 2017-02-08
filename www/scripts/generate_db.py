#!/usr/bin/python

# This script has to generate the sqlite database
#
# Requirements (import from):
#   -  sqlite3
#
# Syntax:
#   ./generate_db.py

import sqlite3

import hashlib
import getpass
import sys
from os import path, urandom
SCRIPT_PATH = path.dirname(__file__)
DEFAULT_DB = path.join(SCRIPT_PATH, "../projects.db")

def generate_tables():
    conn = sqlite3.connect(DEFAULT_DB)
    
    with conn:
        c = conn.cursor()
        
        # Drop tables if they exist
        #c.execute('''DROP TABLE IF EXISTS node''')
        #c.execute('''DROP TABLE IF EXISTS expense''')
        #c.execute('''DROP TABLE IF EXISTS node_expense''')
        #c.execute('''DROP TABLE IF EXISTS users''')
        
        # Create tables
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        salt TEXT NOT NULL)''')
        
        # Commit the changes
        conn.commit()

def add_administrator():
    if sys.version_info < (3, 0):
        username = raw_input("Username: ")
    else:
        username = input("Username: ")
    ask_password = True
    while ask_password:
        ask_password = False
        password = getpass.getpass("Enter your password: ")
        cpassword = getpass.getpass("Enter your password (confirmation): ")
        if password != cpassword:
            ask_password = True
            print("Passwords differ")
    conn = sqlite3.connect(DEFAULT_DB)
    with conn:
        c = conn.cursor()
        salt = urandom(16).encode('hex')
        h = hashlib.sha1()
        h.update(salt+password)
        hashvalue= h.hexdigest()
        c.execute('''DELETE FROM users WHERE username=?''', (username,))
        c.execute('''INSERT INTO users (username, password, salt)
                        VALUES (?, ?, ?)''', (username, hashvalue, salt));


if __name__ == '__main__':
    generate_tables()
    add_administrator()

