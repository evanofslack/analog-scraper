import os
from typing import List

import psycopg2

from s3_upload import UploadError, s3_upload


def create_connection(test: bool = False):
    connection = None
    try:
        if not test:
            connection = psycopg2.connect(os.environ.get("DATABASE_URL"))
        elif test:
            connection = psycopg2.connect(
                host=os.environ.get("DBHOST"),
                database=os.environ.get("DBNAME"),
                user=os.environ.get("DBUSER"),
                password=os.environ.get("DBPASSWORD"),
            )
        else:
            raise Exception("Must set database init")
        return connection
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def create_table(connection):

    create_picture_table = """CREATE TABLE IF NOT EXISTS pictures (
                            id SERIAL PRIMARY KEY, 
                            url text NOT NULL UNIQUE, 
                            title text, 
                            author text,
                            permalink text,
                            score integer,
                            nsfw boolean,
                            greyscale boolean,
                            time integer,
                            width integer,
                            height integer
                            );"""
    try:
        c = connection.cursor()
        c.execute(create_picture_table)
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def create_picture(conn, s3, data: tuple):
    try:
        c = conn.cursor()
        c.execute(
            """
            INSERT 
            INTO pictures(url, title, author, permalink, score, nsfw, greyscale, time, width, height, sprocket, lowUrl, lowWidth, lowHeight, medUrl, medWidth, medHeight, highUrl, highWidth, highHeight) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON CONFLICT (permalink) DO NOTHING
            RETURNING id,url
            """,
            data,
        )

        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def get_tables(conn):
    cursor = conn.cursor()
    cursor.execute(
        """SELECT table_name FROM information_schema.tables
       WHERE table_schema = 'public'"""
    )
    for table in cursor.fetchall():
        print(table)


def get_columns(conn):
    c = conn.cursor()
    c.execute("Select * FROM pictures LIMIT 0")
    colnames = [desc[0] for desc in c.description]
    print(colnames)


def get_all(conn):
    c = conn.cursor()
    # c.execute("""SELECT * FROM pictures ORDER BY id DESC LIMIT 20""")
    c.execute("""SELECT * FROM pictures ORDER BY id ASC LIMIT 20""")
    row = c.fetchone()

    while row is not None:
        print(row)
        print("\n")
        row = c.fetchone()


def get_latest(conn) -> List[str]:
    c = conn.cursor()
    c.execute("""SELECT title FROM pictures ORDER BY id DESC LIMIT 20""")
    row = c.fetchone()

    titles = []
    while row is not None:
        if row:
            titles.append(row[0])
        row = c.fetchone()

    return titles


def update_url(conn, s3, id, url):
    query = """ UPDATE pictures
                SET url = %s
                WHERE id = %s"""

    c = conn.cursor()
    try:
        new_url = s3_upload(s3, bucket="analog-photos", url=url, filename=id)
    except UploadError:
        return
    c.execute(query, (new_url, id))


if __name__ == "__main__":

    conn = create_connection(True)
    # get_all(conn)
    for p in get_latest(conn):
        print(p)
