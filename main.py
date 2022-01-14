import dataclasses
import time

from postgres import (
    create_connection,
    create_picture,
    create_table,
    get_all,
    get_columns,
    get_tables,
    update_table,
)
from scrape import get_pics


def scrape_analog(conn):
    for data in get_pics(num_pics=7, subreddit="analog"):
        create_picture(conn, dataclasses.astuple(data))


def scrape_bw(conn):
    for data in get_pics(num_pics=2, subreddit="analog_bw"):
        create_picture(conn, dataclasses.astuple(data))


def scrape_sprocket(conn):
    for data in get_pics(num_pics=1, subreddit="SprocketShots"):
        create_picture(conn, dataclasses.astuple(data))


if __name__ == "__main__":
    test = False
    conn = create_connection(test)  # Create DB connection
    update_table(conn)
    get_columns(conn)

    scrape_bw(conn)  # Scrape top black & white picture once a day
    scrape_sprocket(conn)  # Scrape top sprocket shot once a day
    get_all(conn)
    conn.close()

    while True:
        time.sleep(100000000)
        break

    for i in range(3):  # Scrape top analog pictures approximately every 8 hours
        conn = create_connection(test)
        scrape_analog(conn)
        conn.close()
        time.sleep(60 * 60 * 8)  # Wait for 8 hours

    while True:
        # Heroku will restart container approximately every 24 hours
        time.sleep(60 * 60 * 24)
