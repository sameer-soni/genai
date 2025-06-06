import os

def get_weather(city:str):
    if city == "lucknow":
        return "27"
    return "33"

def run_command(cmd:str):
    result = os.system(cmd)
    return result

def write_file(path:str, content:str):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"succesfully written to {path}"
    except:
        return f"failed to write to {path}"
 
def read_file(path:str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"File not found {path}"
    except Exception as e:
        return f"Failed to read {path}: {str(e)}"