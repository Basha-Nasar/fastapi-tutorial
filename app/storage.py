from pathlib import Path
import json


DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "users.json"

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            content = f.read()
            if content.strip():
                return json.loads(content)
    return []



def save_data(data):
    DATA_DIR.mkdir(parents=True, exist_ok= True)
    serializable = [item.model_dump() if hasattr(item, "model_dump") else item for item in data]
    with open(DATA_FILE , 'w') as f:
        json.dump(serializable, f, indent = 2)
        
        
        
def reset_data(data):
    if DATA_FILE.exists():
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    else:
        save_data(data)
    return 


