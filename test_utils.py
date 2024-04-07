import json
from pathlib import Path

PATH = Path("tests/test_data/")

def open_json_file(path):
    with open(path) as f: return json.load(f)

def get_test_data():
   files = PATH.glob("*.json") 
   return [open_json_file(file) for file in files]

if __name__ == '__main__':
    all_files = get_test_data()
