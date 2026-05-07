from pathlib import Path
from setuptools import setup, find_packages

cwd = Path(__file__).resolve().parent


req_path = cwd / 'employee_events' / 'requirements.txt'
if req_path.exists():
    requirements = req_path.read_text().split('\n')
  
    requirements = [r.strip() for r in requirements if r.strip()]
else:
  
    requirements = ['fasthtml', 'pandas', 'plotly', 'numpy', 'matplotlib']

setup_args = dict(
    name='employee_events',
    version='0.1.0',  
    description='SQL Query API and Dashboard Visualizer',
    long_description=(cwd.parent / "README.md").read_text() if (cwd.parent / "README.md").exists() else "",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={'employee_events': ['*.db', 'requirements.txt']},
    include_package_data=True,
    install_requires=requirements,
)

if __name__ == "__main__":
    setup(**setup_args)