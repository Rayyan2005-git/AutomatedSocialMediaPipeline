import json
import os
import datetime

class ManifestWriter:
    def __init__(self, output_path):
        self.output_path = output_path
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

    def write(self, target_date: datetime.date, weekday: str, themes_searched: list, files: list):
        manifest_data = {
            "run_date": target_date.isoformat(),
            "weekday": weekday,
            "themes_searched": themes_searched,
            "files": []
        }

        for f in files:
            manifest_data["files"].append({
                "drive_file_id": f['id'],
                "local_path": f.get('local_path', ''),
                "matched_theme": f.get('matched_theme', ''),
                "mime_type": f['mimeType'],
                "file_name": f['name']
            })

        with open(self.output_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
