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

CURRENT_VERSION = 0

def _generate_table_users(c):
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    salt TEXT NOT NULL)''')

def _generate_table_updates(c):
    c.execute('''CREATE TABLE IF NOT EXISTS updates (
                   name VARCHAR(20) NOT NULL UNIQUE,
                   revision INTEGER NOT NULL)''')

def generate_tables():
    with sqlite3.connect(DEFAULT_DB) as conn:
        c = conn.cursor()
        
        _generate_table_users(c)
        _generate_table_updates(c)
        
        c.execute('''INSERT INTO updates (name, revision) VALUES ('__global__', ?)''', (CURRENT_VERSION,))
        conn.commit()

def migrate_from_django():
    generate_tables()

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
    
    with sqlite3.connect(DEFAULT_DB) as conn:
        c = conn.cursor()
        salt = urandom(16).encode('hex')
        h = hashlib.sha1()
        h.update(salt+password)
        hashvalue= h.hexdigest()
        c.execute('''DELETE FROM users WHERE username=?''', (username,))
        c.execute('''INSERT INTO users (username, password, salt)
                        VALUES (?, ?, ?)''', (username, hashvalue, salt))
        conn.commit()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Syntax error: takes at least one parameter (init/migrate/adduser)")
        exit(1)
    
    op = sys.argv[1]
    if op == "init":
        generate_tables()
    elif op == "migrate":
        migrate_from_django()
    elif op == "adduser":
        add_administrator()

