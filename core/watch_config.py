import json
import os

class WatchConfig:
    """Manages watched folder configurations"""
    
    def __init__(self, config_path='config/settings.json'):
        self.config_path = config_path
        self.watched_folders = []
        self.load()
    
    def load(self):
        """Load watched folders from config"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.watched_folders = data.get('watchedFolders', [])
        except Exception as e:
            print(f"Error loading watch config: {e}")
            self.watched_folders = []
    
    def save(self):
        """Save watched folders to config"""
        try:
            config_data = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
            
            config_data['watchedFolders'] = self.watched_folders
            
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            print(f"Error saving watch config: {e}")
    
    def add_folder(self, path, preset_id, auto_process=True, output_folder='', delete_original=False):
        """Add a watched folder"""
        for folder in self.watched_folders:
            if folder['path'] == path:
                return False
        
        self.watched_folders.append({
            'path': path,
            'presetId': preset_id,
            'autoProcess': auto_process,
            'outputFolder': output_folder,
            'deleteOriginal': delete_original,  # NEW
            'enabled': True
        })
        self.save()
        return True

    
    def remove_folder(self, path):
        """Remove a watched folder"""
        self.watched_folders = [f for f in self.watched_folders if f['path'] != path]
        self.save()
    
    def update_folder(self, path, **kwargs):
        """Update a watched folder config"""
        for folder in self.watched_folders:
            if folder['path'] == path:
                folder.update(kwargs)
                self.save()
                return True
        return False
    
    def get_enabled_folders(self):
        """Get all enabled watched folders"""
        return [f for f in self.watched_folders if f.get('enabled', True)]
