from sqlite3 import connect
from pathlib import Path
from functools import wraps
import pandas as pd

# Absolute path to the database
db_path = Path(__file__).resolve().parent / "employee_events.db"

class SQLExecutionMixin:
    
    def pandas_query(self, sql_query):
        """الاستعلام باستخدام pandas لإرجاع DataFrame"""
        connection = connect(db_path)
        try:
            return pd.read_sql_query(sql_query, connection)
        finally:
            connection.close()

    # أضف هذا السطر تحديداً لحل مشكلة الـ AttributeError
    # هو مجرد اسم مستعار لكي يفهم ملف employee.py الطلب
    run_query = pandas_query

    def query(self, sql_query):
        """الاستعلام العادي لإرجاع قائمة من الـ tuples"""
        connection = connect(db_path)
        try:
            cursor = connection.cursor()
            result = cursor.execute(sql_query).fetchall()
            return result
        finally:
            connection.close()

# كود الـ Decorator يبقى كما هو بالأسفل...
def query(func):
    @wraps(func)
    def run_query(*args, **kwargs):
        query_string = func(*args, **kwargs)
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(query_string).fetchall()
        connection.close()
        return result
    return run_query