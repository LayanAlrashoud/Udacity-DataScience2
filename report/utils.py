import pickle
from pathlib import Path

# Using the Path object, create a `project_root` variable
# set to the absolute path for the root of this project directory
# .resolve() gets the full Windows path, and .parent.parent moves up to the root
project_root = Path(__file__).resolve().parent.parent

# Using the `project_root` variable
# create a `model_path` variable
# that points to the file `model.pkl` inside the assets directory
# The / operator works here because project_root is a Path object
model_path = project_root / 'assets' / 'model.pkl'

def load_model():
    """
    Unpickles the machine learning model from the assets directory.
    """
    with model_path.open('rb') as file:
        model = pickle.load(file)

    return model