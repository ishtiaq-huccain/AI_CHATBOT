
import csv
import sqlite3

def create_table():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (ID TEXT PRIMARY KEY, Title TEXT, Price TEXT, Brand TEXT, rating TEXT, review TEXT)''')
    conn.close()

def load_csv(filename):
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    
    with open(filename, 'r',encoding ="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # skip header
        
        for row in csvreader:
            ID, Title, Price, Brand, rating, review = row
            c.execute("INSERT INTO products (ID, Title, Price, Brand, rating, review) VALUES (?, ?, ?, ?, ?, ?)",
                      (ID, Title, Price, Brand, rating, review))
            
    conn.commit()
    conn.close()

create_table()
load_csv('products.csv')
