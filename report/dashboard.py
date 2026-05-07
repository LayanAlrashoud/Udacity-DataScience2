import pandas as pd
import numpy as np
import plotly.express as px
from typing import Union, List, Any

from fasthtml.common import (
    FastHTML, serve, Link, H1, Div,
    Request, RedirectResponse, StaticFiles, NotStr
)

from employee_events import QueryBase, Employee, Team
from utils import load_model
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    DataTable
)
from combined_components import FormGroup, CombinedComponent


# --- App Initialization ---
app: FastHTML = FastHTML(hdrs=(
    Link(rel="stylesheet", href="/assets/report.css"),
))

app.mount("/assets", StaticFiles(directory="assets"))


# --- Component Classes ---


class ReportDropdown(Dropdown):
    """Component for selecting employees or teams from a dropdown menu."""

    def build_component(self, entity_id: Any, model: QueryBase) -> Any:
        self.label: str = model.name.title()
        return super().build_component(entity_id, model)

    def component_data(self, entity_id: Any, model: QueryBase) -> List[Any]:
        return model.names()


class Header(BaseComponent):
    """Renders the main title of the dashboard."""

    def build_component(self, entity_id: Any, model: QueryBase) -> H1:
        return H1(model.name.title())


class LineChart(BaseComponent):
    """Renders an interactive Line Chart using Plotly."""

    def build_component(
        self, entity_id: Union[int, str], mod: QueryBase
    ) -> Any:
        df: pd.DataFrame = mod.event_counts(entity_id)

        if df.empty:
            return Div(
                "No Event Data Found",
                style="text-align: center; padding: 20px; color: gray;"
            )

        df = df.fillna(0)
        df['positive_events'] = pd.to_numeric(df['positive_events'])
        df['negative_events'] = pd.to_numeric(df['negative_events'])
        df = df.set_index('event_date').sort_index()
        df = df[['positive_events', 'negative_events']].cumsum().reset_index()

        fig = px.line(
            df,
            x='event_date',
            y=['positive_events', 'negative_events'],
            labels={
                'value': 'Count',
                'event_date': 'Date',
                'variable': 'Type'
            },
            title='Cumulative Performance Trends'
        )

        fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=350)

        html_str = fig.to_html(full_html=False, include_plotlyjs='cdn')
        return Div(NotStr(html_str))


class BarChart(BaseComponent):
    """Renders an interactive Risk Analysis Bar Chart using Plotly."""
    predictor: Any = load_model()

    def build_component(
        self, entity_id: Union[int, str], mod: QueryBase
    ) -> Any:
        data: pd.DataFrame = mod.model_data(entity_id)

        if data.empty:
            return Div(
                "No prediction data available",
                style="text-align: center; color: gray;"
            )

        probs: np.ndarray = self.predictor.predict_proba(data)
        is_team = mod.name == "team"
        pred: float = float(probs[:, 1].mean() if is_team else probs[0, 1])

        if pred < 0.4:
            color: str = '#22c55e'
        elif pred < 0.7:
            color: str = '#f59e0b'
        else:
            color: str = '#ef4444'

        fig = px.bar(
            x=[pred],
            y=["Risk Score"],
            orientation='h',
            range_x=[0, 1],
            color_discrete_sequence=[color],
            title=f"Predicted Risk: {pred:.1%}"
        )

        fig.update_layout(height=200, margin=dict(l=20, r=20, t=50, b=20))

        html_str = fig.to_html(full_html=False, include_plotlyjs='cdn')
        return Div(NotStr(html_str))


class Visualizations(CombinedComponent):
    """Grid layout for various charts."""
    children: List[Any] = [LineChart(), BarChart()]
    outer_div_type: Div = Div(cls='grid')


class NotesTable(DataTable):
    """Renders a data table for specific notes."""

    def component_data(
        self, entity_id: Union[int, str], mod: QueryBase
    ) -> Any:
        return mod.notes(entity_id)


class DashboardFilters(FormGroup):
    """Form filters to toggle between Employee and Team views."""
    id: str = "top-filters"
    action: str = "/update_data"
    method: str = "POST"
    children: List[Any] = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
        ),
        ReportDropdown(id="selector", name="user-selection")
    ]


class Report(CombinedComponent):
    """Main Report layout structure."""
    children: List[Any] = [
        Header(), DashboardFilters(), Visualizations(), NotesTable()
    ]


# Initialize Report
report: Report = Report()


# --- Routes ---


@app.get("/")
def get() -> Any:
    return report(1, Employee())


@app.get("/employee/{id}")
def get_employee(id: Union[int, str]) -> Any:
    return report(id, Employee())


@app.get("/team/{id}")
def get_team(id: Union[int, str]) -> Any:
    return report(id, Team())


@app.get('/update_dropdown')
def update_dropdown(profile_type: str) -> Any:
    dropdown: Any = DashboardFilters.children[1]
    if profile_type == 'Team':
        return dropdown(None, Team())
    return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r: Request) -> RedirectResponse:
    data: Any = await r.form()
    profile_type: str = data.get('profile_type')
    selected_id: str = data.get('user-selection')

    path: str = "employee" if profile_type == 'Employee' else "team"
    return RedirectResponse(f"/{path}/{selected_id}", status_code=303)


if __name__ == "__main__":
    serve()
    