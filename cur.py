
import streamlit as st
import sqlite3
import os

# Function to create a table if it doesn't exist
def create_table():
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    create_table_query = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL
    );
    '''

    cursor.execute(create_table_query)
    conn.commit()
    conn.close()

# Function to insert data into the table
def insert_data(username, email):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    insert_query = 'INSERT INTO users (username, email) VALUES (?, ?);'
    cursor.execute(insert_query, (username, email))

    conn.commit()
    conn.close()

# Function to fetch data from the table
def fetch_data():
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    fetch_query = 'SELECT * FROM users;'
    cursor.execute(fetch_query)
    data = cursor.fetchall()

    conn.close()
    return data

# Check if the database file exists; if not, create it and the table
if not os.path.exists('example.db'):
    create_table()

# Streamlit app
def main():
    st.title('SQLite Database Example')

    # User input for inserting data
    username = st.text_input('Enter username:')
    email = st.text_input('Enter email:')
    
    # Insert data when the user clicks the button
    if st.button('Insert Data'):
        insert_data(username, email)

    # Display the data in a Streamlit table
    st.header('User Data')
    data = fetch_data()
    st.table(data)

if __name__ == '__main__':
    main()

