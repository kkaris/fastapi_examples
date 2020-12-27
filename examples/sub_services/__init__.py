from os import environ
from pathlib import Path

# Set data directory
if environ.get('DATA_DIR'):
    DATA_DIR = Path(environ['DATA_DIR']).absolute()
else:
    HERE = Path(__file__).parent.absolute()  # This dir
    DATA_DIR = HERE.parent.joinpath('data')  # Directory in parent dir

if not DATA_DIR.is_dir():
    DATA_DIR.mkdir(parents=True)
