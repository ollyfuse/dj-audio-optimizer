import json
import os

class PresetManager:
    def __init__(self):
        self.presets = {}
        self.load_presets()
    
    def load_presets(self):
        preset_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'presets.json')
        with open(preset_file, 'r') as f:
            self.presets = json.load(f)
    
    def get_preset(self, name):
        return self.presets.get(name, self.presets['club_festival'])
    
    def get_all_presets(self):
        return self.presets
