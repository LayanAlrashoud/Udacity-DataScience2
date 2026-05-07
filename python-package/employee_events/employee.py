from typing import List, Tuple, Any
import pandas as pd
from .query_base import QueryBase
from .sql_execution import SQLExecutionMixin

class Employee(QueryBase):
    """
    Employee class to handle specific database queries for employee data.
    """
    
    # Class attribute for the table name
    name: str = "employee"

    def names(self) -> List[Tuple[str, int]]:
        """
        Retrieves a list of all employees' full names and their IDs.
        Returns:
            List[Tuple[str, int]]: A list containing tuples of (full_name, employee_id).
        """
        query: str = f"SELECT first_name || ' ' || last_name, employee_id FROM {self.name}"
        
        # We use run_query and convert the result to a list of tuples
        result_df: pd.DataFrame = self.run_query(query)
        return list(result_df.itertuples(index=False, name=None))

    def username(self, employee_id: int) -> List[Tuple[str]]:
        """
        Retrieves the full name of a specific employee by their ID.
        Args:
            employee_id (int): The unique identifier for the employee.
        Returns:
            List[Tuple[str]]: A list containing a tuple with the employee's full name.
        """
        query: str = f"SELECT first_name || ' ' || last_name FROM {self.name} WHERE employee_id = {employee_id}"
        
        result_df: pd.DataFrame = self.run_query(query)
        return list(result_df.itertuples(index=False, name=None))

    def model_data(self, employee_id: int) -> pd.DataFrame:
        """
        Generates aggregated event data for machine learning models.
        Args:
            employee_id (int): The unique identifier for the employee.
        Returns:
            pd.DataFrame: A DataFrame containing positive and negative event sums.
        """
        sql_text: str = f"""
                    SELECT SUM(positive_events) AS positive_events
                         , SUM(negative_events) AS negative_events
                    FROM {self.name}
                    JOIN employee_events
                        USING({self.name}_id)
                    WHERE {self.name}.{self.name}_id = {employee_id}
                """
        return self.run_query(sql_text)