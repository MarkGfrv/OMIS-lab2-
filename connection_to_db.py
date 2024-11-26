import psycopg2
from psycopg2 import sql
from contextlib import contextmanager

db_config = {
    'dbname': 'postgres',
    'password': '5595515m',
    'user': 'postgres',
    'host': 'localhost',
    'port': 5432,
}

@contextmanager
def database_connection():
    connection = psycopg2.connect(**db_config)
    try:
        yield connection
    finally:
        connection.close()

class Database:
    @staticmethod
    def call_procedure(procedure_name, *params):
        with database_connection() as connection:
            with connection.cursor() as cursor:
                query = sql.SQL("CALL {}({})").format(
                    sql.Identifier(procedure_name),
                    sql.SQL(', ').join(map(sql.Literal, params))
                )
                cursor.execute(query)
                connection.commit()

    @staticmethod
    def fetch_function(function_name, *params):
        with database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql.SQL("SELECT {}({})").format(
                    sql.Identifier(function_name),
                    sql.SQL(', ').join(map(sql.Literal, params))
                ))
                results = cursor.fetchall()
                return results if results else None

    @staticmethod
    def execute_query(query, params = None, fetch = False):
        with database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                connection.commit()


