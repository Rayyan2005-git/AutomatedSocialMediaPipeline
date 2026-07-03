import datetime

class SheetThemeSelector:
    def __init__(self, sheet_rows):
        self.rows = sheet_rows

    def get_theme_for_date(self, target_date: datetime.date):
        """
        Parses the sheet rows and returns the theme for the exact date.
        Rows are expected to be lists where:
        index 0: Date
        index 1: Product folder (optional, falls back to Theme)
        index 2: Theme
        index 3: Prompt (optional, falls back to Theme)
        """
        target_str = target_date.isoformat()
        
        for row in self.rows:
            if not row:
                continue
            
            # Check if Date column exists and matches
            if len(row) > 0 and row[0].strip() == target_str:
                # Get Product folder (index 1)
                product_folder = None
                if len(row) > 1 and row[1].strip():
                    product_folder = row[1].strip()
                    
                # Get Theme (index 2)
                if len(row) > 2 and row[2].strip():
                    theme = row[2].strip()
                else:
                    return None, None, f"Theme cell is empty for date {target_str}."
                    
                # If product folder was empty, fallback to Theme
                if not product_folder:
                    product_folder = theme
                    
                # Get Prompt (index 3)
                prompt = theme
                if len(row) > 3 and row[3].strip():
                    prompt = row[3].strip()
                    
                return theme, prompt, product_folder, None
        
        return None, None, None, f"Date {target_str} not found in the Google Sheet."

    def filter_files(self, files, theme, prompt, is_subfolder=False):
        """
        Filters files matching the exact theme in their name.
        If is_subfolder is True, accepts all files in the subfolder.
        Matches are case-insensitive.
        """
        if not theme:
            return []
            
        matched_files = []
        for f in files:
            name_lower = f['name'].lower()
            if is_subfolder or theme.lower() in name_lower:
                f['matched_theme'] = theme
                f['generation_prompt'] = prompt
                matched_files.append(f)
                    
        return matched_files
