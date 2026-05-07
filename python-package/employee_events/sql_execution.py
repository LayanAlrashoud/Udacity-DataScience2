from sqlite3 import connect
from pathlib import Path
from functools import wraps
from typing import List, Any
import pandas as pd

# Absolute path to the database
DB_PATH: Path = Path(__file__).resolve().parent / "employee_events.db"


class SQLExecutionMixin:
    """
    Mixin class to handle SQL executions using both standard
    sqlite3 and pandas.
    """

    def pandas_query(self, sql_query: str) -> pd.DataFrame:
        """Executes a query and returns a pandas DataFrame."""
        with connect(DB_PATH) as connection:
            return pd.read_sql_query(sql_query, connection)

    def query(self, sql_query: str) -> List[Any]:
        """Executes a query and returns a list of tuples."""
        with connect(DB_PATH) as connection:
            cursor = connection.cursor()
            return cursor.execute(sql_query).fetchall()

    run_query = pandas_query


def query_decorator(func):
    """
    Decorator to execute a SQL query returned by the decorated function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> List[Any]:
        query_string: str = func(*args, **kwargs)
        with connect(DB_PATH) as connection:
            cursor = connection.cursor()
            result = cursor.execute(query_string).fetchall()
            return result
    return wrapper