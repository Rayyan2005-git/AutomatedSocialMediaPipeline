import datetime

class SheetThemeSelector:
    def __init__(self, sheet_rows):
        self.rows = sheet_rows

    def get_theme_for_date(self, target_date: datetime.date):
        """
        Parses the sheet rows and returns the theme for the exact date.
        Rows are expected to be lists where index 0 is Date, index 1 is Theme.
        Returns:
            theme (str): The theme if found and not empty.
            error (str): An error message if not found or empty.
        """
        target_str = target_date.isoformat()
        
        for row in self.rows:
            if not row:
                continue
            
            # Check if Date column exists and matches
            if len(row) > 0 and row[0].strip() == target_str:
                # We found the date. Now check the theme and prompt.
                if len(row) > 1 and row[1].strip():
                    theme = row[1].strip()
                else:
                    return None, None, f"Theme cell is empty for date {target_str}."
                    
                if len(row) > 2 and row[2].strip():
                    prompt = row[2].strip()
                else:
                    return None, None, f"Generation Prompt cell is empty for date {target_str}."
                    
                return theme, prompt, None
        
        return None, None, f"Date {target_str} not found in the Google Sheet."

    def filter_files(self, files, theme, prompt):
        """
        Filters files matching the exact theme in their name.
        Matches are case-insensitive.
        """
        if not theme:
            return []
            
        matched_files = []
        for f in files:
            name_lower = f['name'].lower()
            if theme.lower() in name_lower:
                f['matched_theme'] = theme
                f['generation_prompt'] = prompt
                matched_files.append(f)
                    
        return matched_files
