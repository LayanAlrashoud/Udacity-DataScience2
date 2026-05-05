# Import any dependencies needed to execute sql queries
from .sql_execution import SQLExecutionMixin

# Define a class called QueryBase
# Use inheritance to add methods
# for querying the employee_events database.
class QueryBase(SQLExecutionMixin):

    # Create a class attribute called `name`
    # set the attribute to an empty string
    name = ""

    # Define a `names` method that receives
    # no passed arguments
    def names(self):
        
        # Return an empty list
        return []


    # Define an `event_counts` method
    # that receives an `entity_id` argument
    # This method should return a pandas dataframe
    def event_counts(self, entity_id):

        # QUERY 1
        # Write an SQL query that groups by `event_date`
        # and sums the number of positive and negative events
        # Use f-string formatting to set the FROM {table}
        # to the `name` class attribute
        # Use f-string formatting to set the name
        # of id columns used for joining
        # order by the event_date column
        query = f"""
            SELECT 
                event_date, 
                SUM(positive_events) AS positive_events, 
                SUM(negative_events) AS negative_events
            FROM {self.name}
            JOIN employee_events USING({self.name}_id)
            WHERE {self.name}_id = {entity_id}
            GROUP BY event_date
            ORDER BY event_date ASC
        """
        
        return self.run_query(query)
    
    # This method is required for the BarChart prediction logic
    def model_data(self, entity_id):
        query = f"""
            SELECT positive_events, negative_events
            FROM {self.name}
            JOIN employee_events USING({self.name}_id)
            WHERE {self.name}_id = {entity_id}
        """
        return self.run_query(query)
    

    # Define a `notes` method that receives an entity_id argument
    # This function should return a pandas dataframe
    def notes(self, entity_id):

        # QUERY 2
        # Write an SQL query that returns `note_date`, and `note`
        # from the `notes` table
        # Set the joined table names and id columns
        # with f-string formatting
        # so the query returns the notes
        # for the table name in the `name` class attribute
        query = f"""
            SELECT note_date, note
            FROM notes
            JOIN {self.name} USING({self.name}_id)
            WHERE {self.name}_id = {entity_id}
        """
        
        return self.run_query(query)