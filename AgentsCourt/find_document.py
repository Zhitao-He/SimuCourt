import os
import json
from tqdm import tqdm  

def find_value_by_id_in_folder_with_progress(folder_path, target_id):
    files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    total_files = len(files)

    # Iterate through all the files with a progress bar
    for file in tqdm(files, desc="Searching files"):
        file_path = os.path.join(folder_path, file)

        # Open and read the json file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check if the target id is in this json file
            if target_id in data:
                return data[target_id]  # Return the value if found
        except json.JSONDecodeError as e:
            print(f"Error reading {file_path}: {e}")

    return None  # Return None if the id is not found in any file





