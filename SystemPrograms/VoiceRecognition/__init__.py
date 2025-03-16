import os
import importlib

# Get the directory path of the current module
module_dir = os.path.dirname(__file__)

# Iterate over all Python files in the directory
for file in os.listdir(module_dir):
    if file.endswith(".py") and file != "__init__.py":
        module_name = file[:-3]  # Remove .py extension
        importlib.import_module(f"{__name__}.{module_name}")
