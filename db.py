import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="trolley.proxy.rlwy.net",
        user="root",
        password="orMxwOZWScBYDyXxqIqYqjQQriyOHNkk",
        database="railway",
        port=11667
    )
