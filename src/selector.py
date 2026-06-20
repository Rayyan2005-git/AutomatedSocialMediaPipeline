import json
import datetime

class ThemeSelector:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.themes_config = json.load(f)

    def get_themes_for_date(self, target_date: datetime.date):
        weekday_name = target_date.strftime("%A")
        return weekday_name, self.themes_config.get(weekday_name, [])

    def filter_files(self, files, themes):
        """
        Filters files matching any of the themes in their name.
        Matches are case-insensitive.
        """
        if not themes:
            return []
            
        matched_files = []
        for f in files:
            name_lower = f['name'].lower()
            for theme in themes:
                if theme.lower() in name_lower:
                    f['matched_theme'] = theme
                    matched_files.append(f)
                    break # Match only the first theme found
                    
        return matched_files
