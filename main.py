
from src.data_collection.crawler_bds import crawler_and_load_data
from database.connect_db import connect

def main():
    crawler_and_load_data()

if __name__ == "__main__":
    main()