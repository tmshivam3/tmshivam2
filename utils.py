import os

def list_subfolders(directory):
    try:
        return [f.name for f in os.scandir(directory) if f.is_dir()]
    except FileNotFoundError:
        print(f"Directory {directory} not found.")
        return []

def generate_preview(year, theme, new_value):
    print("DEBUG: generate_preview() was called!")
    print(f"Inputs => year: {year}, theme: {theme}, new_value: {new_value}")

    preview = f"Preview for {year} - Theme: {theme} - Value: {new_value}"
    print("Generated Preview:", preview)
    return preview
