import psycopg2
from psycopg2 import OperationalError
import os
import sys
from typing import Dict, Any, Optional, Tuple

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


def connect_to_postgresql(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        print("Connection to PostgreSQL DB successful")
        return connection
    except OperationalError as e:
        print(f" The error '{e}' occurred")
        return None


def insert_epaper(epaper_name: str, date: str, file_path: str) -> None:
    connection = None
    cursor = None

    try:
        connection = connect_to_postgresql(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)

        if not connection:
            return None

        insert_sql = """
                     INSERT INTO epaper_catalog (epaper_name, date, file_path)
                     VALUES (%s, %s, %s);
                     """
        params: Tuple[str, str, str] = (epaper_name, date, file_path)

        cursor = connection.cursor()
        cursor.execute(insert_sql, params)
        connection.commit()


    except OperationalError as e:
        print(f"Database Operational Error during insert: {e}")
        if connection:
            connection.rollback()
        return None

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def get_details(epaper_name: str, date: str) -> Optional[Dict[str, Any]]:
    connection = None
    cursor = None

    try:
        connection = connect_to_postgresql(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)

        if not connection:
            return None

        query = """
                SELECT file_path
                FROM epaper_catalog
                WHERE epaper_name = %s
                  AND date = %s; 
                """
        params = (epaper_name, date)

        cursor = connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()

        if result:
            file_path = result[0]
            return {"file_path": file_path}
        else:
            return None

    except OperationalError as e:
        print(f"Database Operational Error: {e}")
        if connection:
            connection.rollback()
        return None

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("Connection closed.")

