import json
import os
from pathlib import Path

def profile_reference_data(ref_dir: str, output_path: str):
    ref_path = Path(ref_dir)
    stats = {
        "files": {}
    }
    
    if not ref_path.exists():
        print(f"Directory {ref_dir} does not exist.")
        return
        
    for file in ref_path.glob("*.*"):
        stats["files"][file.name] = {
            "size_bytes": os.path.getsize(file),
        }
        
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(stats, f, indent=2)

if __name__ == "__main__":
    profile_reference_data(
        "../../../data/reference", 
        "../../../data/reference_profile.json"
    )
