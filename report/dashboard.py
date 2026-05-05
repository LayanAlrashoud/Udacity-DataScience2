import pandas as pd
import matplotlib.pyplot as plt
from fasthtml.common import *
from fasthtml import FastHTML, serve
from starlette.staticfiles import StaticFiles

# Import QueryBase, Employee, Team from employee_events
from employee_events import QueryBase, Employee, Team

# import the load_model function from the utils.py file
from utils import load_model

"""
Below, we import the parent classes
you will use for subclassing
"""
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
    )

from combined_components import FormGroup, CombinedComponent

# Initialize a fasthtml app 
app = FastHTML(hdrs=(
    Link(rel="stylesheet", href="/assets/report.css"),
))

app.mount("/assets", StaticFiles(directory="assets"))

# Create a subclass of base_components/dropdown
# called `ReportDropdown`
class ReportDropdown(Dropdown):
    
    # Overwrite the build_component method
    # ensuring it has the same parameters
    def build_component(self, entity_id, model):
        # Set the `label` attribute so it is set
        # to the `name` attribute for the model
        self.label = model.name
        
        # Return the output from the
        # parent class's build_component method
        return super().build_component(entity_id, model)
    
    # Overwrite the `component_data` method
    def component_data(self, entity_id, model):
        # Using the model argument
        # call the employee_events method
        return model.names()


# Create a subclass of base_components/BaseComponent
# called `Header`
class Header(BaseComponent):

    # Overwrite the `build_component` method
    def build_component(self, entity_id, model):
        
        # Using the model argument for this method
        # return a fasthtml H1 objects
        return H1(model.name.title())
          

# Create a subclass of base_components/MatplotlibViz
# called `LineChart`
class LineChart(MatplotlibViz):
    
    # Changed parameter name to `entity_id` to match Developer Guide
    def visualization(self, entity_id, model):
        # Fetch event counts
        df = model.event_counts(entity_id)
        
        # 1. Check if the dataframe is empty to avoid crashing
        if df.empty:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, 'No Event Data Found', 
                    horizontalalignment='center', verticalalignment='center')
            self.set_axis_styling(ax, bordercolor='black', fontcolor='black')
            return

        # 2. Fill nulls and ensure numeric types
        df = df.fillna(0)
        df['positive_events'] = pd.to_numeric(df['positive_events'])
        df['negative_events'] = pd.to_numeric(df['negative_events'])
        
        # 3. Process data for plotting
        df = df.set_index('event_date')
        df = df.sort_index()
        
        # Cumulative sum for the trends
        df = df[['positive_events', 'negative_events']].cumsum()
        df.columns = ['Positive', 'Negative']
        
        # 4. Initialize and plot
        fig, ax = plt.subplots(figsize=(10, 4))
        df.plot(ax=ax)
        
        # Set styling and labels
        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')
        ax.set_title('Cumulative Performance Events')
        ax.set_xlabel('Date')
        ax.set_ylabel('Cumulative Count')

# Create a subclass of base_components/MatplotlibViz
# called `BarChart`
class BarChart(MatplotlibViz):
    predictor = load_model()

    # Changed parameter name to `entity_id` to match Developer Guide
    def visualization(self, entity_id, model):
        # Fetch the data
        data = model.model_data(entity_id)
        
        # Handling empty data gracefully
        if data.empty:
            fig, ax = plt.subplots(figsize=(10, 2))
            ax.text(0.5, 0.5, 'No data available for risk prediction', 
                    ha='center', va='center', fontsize=12, color='gray')
            ax.set_axis_off()
            return

        # Run prediction
        probs = self.predictor.predict_proba(data)
        risk_column = probs[:, 1]
        pred = risk_column.mean() if model.name == "team" else risk_column[0]
       
        color = '#22c55e' if pred < 0.4 else '#f59e0b' if pred < 0.7 else '#ef4444'
        
        fig, ax = plt.subplots(figsize=(10, 4))
        
        bar = ax.barh(['Risk Score'], [pred], color=color, height=0.5)
       
        ax.text(pred + 0.01, 0, f'{pred:.1%}', va='center', 
                fontsize=14, fontweight='bold', color=color)
        
        ax.set_xlim(0, 1)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
        
        self.set_axis_styling(ax, bordercolor='#333333', fontcolor='#333333')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        ax.set_title('Predicted Recruitment Risk Analysis', fontsize=16, pad=15)
        plt.tight_layout()

class Visualizations(CombinedComponent):

    # Set the `children` to initialized instances
    children = [LineChart(), BarChart()]

    # Leave this line unchanged
    outer_div_type = Div(cls='grid')
            
# Create a subclass of base_components/DataTable
# called `NotesTable`
class NotesTable(DataTable):

    # Overwrite the `component_data` method
    def component_data(self, entity_id, model):
        # Using the model and entity_id arguments
        return model.notes(entity_id)
    

class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method="POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
            ),
        ReportDropdown(
            id="selector",
            name="user-selection")
        ]
    
# Create a subclass of CombinedComponents
# called `Report`
class Report(CombinedComponent):

    # Sorted in the order they should appear
    children = [Header(), DashboardFilters(), Visualizations(), NotesTable()]

# Initialize the `Report` class
report = Report()


# Create a route for a get request
@app.get("/")
def get():

    # Call the initialized report
    return report(1, Employee())

# Create a route for a get request for an employee ID
@app.get("/employee/{id}")
def get_employee(id: str):

    # Call the initialized report
    return report(id, Employee())

# Create a route for a get request for a team ID
@app.get("/team/{id}")
def get_team(id: str):

    # Call the initialized report
    return report(id, Team())


# Keep the below code unchanged!
@app.get('/update_dropdown')
def update_dropdown(profile_type: str):
    dropdown = DashboardFilters.children[1]
    if profile_type == 'Team':
        return dropdown(None, Team())
    elif profile_type == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)
    
serve()