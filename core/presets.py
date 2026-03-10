import json
import os
from copy import deepcopy

class PresetManager:
    """Manages default and custom presets with validation"""
    
    # Default presets are locked and cannot be edited/deleted
    DEFAULT_PRESETS = ['club_festival', 'bar_lounge', 'radio_broadcast', 'streaming_safe']
    
    def __init__(self):
        self.presets = {}  # Default presets
        self.custom_presets = {}  # User-created presets
        self.config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        self.presets_file = os.path.join(self.config_dir, 'presets.json')
        self.custom_presets_file = os.path.join(self.config_dir, 'custom_presets.json')
        self.load_presets()
    
    def load_presets(self):
        """Load default and custom presets"""
        # Load default presets
        with open(self.presets_file, 'r') as f:
            self.presets = json.load(f)
        
        # Load custom presets if file exists
        if os.path.exists(self.custom_presets_file):
            try:
                with open(self.custom_presets_file, 'r') as f:
                    self.custom_presets = json.load(f)
            except:
                self.custom_presets = {}
    
    def save_custom_presets(self):
        """Save custom presets to file"""
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.custom_presets_file, 'w') as f:
            json.dump(self.custom_presets, f, indent=2)
    
    def get_preset(self, name):
        """Get preset by name (checks custom first, then default)"""
        if name in self.custom_presets:
            return self.custom_presets[name]
        return self.presets.get(name, self.presets['club_festival'])
    
    def get_all_presets(self):
        """Get all presets (default + custom merged)"""
        return {**self.presets, **self.custom_presets}
    
    def get_preset_list(self):
        """Get list of presets with metadata for UI"""
        result = []
        # Add default presets
        for key, preset in self.presets.items():
            result.append({
                'id': key,
                'label': preset['label'],
                'custom': False,
                'locked': True
            })
        # Add custom presets
        for key, preset in self.custom_presets.items():
            result.append({
                'id': key,
                'label': preset.get('label', key),
                'custom': True,
                'locked': False
            })
        return result
    
    def validate_preset(self, preset_data):
        """
        Validate preset parameters for safety
        Returns: {'valid': bool, 'errors': [], 'warnings': []}
        """
        warnings = []
        errors = []
        
        # LUFS validation (-18 to -6 safe range)
        lufs = preset_data.get('target_lufs', -12.0)
        if lufs < -18:
            errors.append("Target LUFS too quiet (min: -18 LUFS)")
        elif lufs > -6:
            errors.append("Target LUFS too loud (max: -6 LUFS)")
        elif lufs > -7:
            warnings.append("Very aggressive LUFS - may cause distortion")
        
        # True peak validation (-1.5 to -0.3 safe range)
        peak = preset_data.get('true_peak', -1.0)
        if peak < -1.5:
            warnings.append("True peak very low - may reduce loudness")
        elif peak > -0.3:
            errors.append("True peak too high (max: -0.3 dB)")
        
        # Highpass validation (20-50 Hz typical range)
        highpass = preset_data.get('highpass_hz', 30)
        if highpass < 20 or highpass > 50:
            warnings.append("Highpass filter outside typical range (20-50 Hz)")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def create_preset(self, preset_id, preset_data):
        """Create new custom preset"""
        # Prevent overwriting default presets
        if preset_id in self.DEFAULT_PRESETS:
            return {'success': False, 'error': 'Cannot overwrite default preset'}
        
        # Validate parameters
        validation = self.validate_preset(preset_data)
        if not validation['valid']:
            return {'success': False, 'error': validation['errors'][0]}
        
        # Save custom preset
        self.custom_presets[preset_id] = preset_data
        self.save_custom_presets()
        return {'success': True, 'warnings': validation['warnings']}
    
    def update_preset(self, preset_id, preset_data):
        """Update existing custom preset"""
        if preset_id in self.DEFAULT_PRESETS:
            return {'success': False, 'error': 'Cannot modify default preset'}
        
        if preset_id not in self.custom_presets:
            return {'success': False, 'error': 'Preset not found'}
        
        validation = self.validate_preset(preset_data)
        if not validation['valid']:
            return {'success': False, 'error': validation['errors'][0]}
        
        self.custom_presets[preset_id] = preset_data
        self.save_custom_presets()
        return {'success': True, 'warnings': validation['warnings']}
    
    def delete_preset(self, preset_id):
        """Delete custom preset"""
        if preset_id in self.DEFAULT_PRESETS:
            return {'success': False, 'error': 'Cannot delete default preset'}
        
        if preset_id in self.custom_presets:
            del self.custom_presets[preset_id]
            self.save_custom_presets()
            return {'success': True}
        
        return {'success': False, 'error': 'Preset not found'}
    
    def duplicate_preset(self, source_id, new_id, new_label):
        """Duplicate existing preset (default or custom)"""
        source = self.get_preset(source_id)
        if not source:
            return {'success': False, 'error': 'Source preset not found'}
        
        if new_id in self.custom_presets or new_id in self.DEFAULT_PRESETS:
            return {'success': False, 'error': 'Preset ID already exists'}
        
        # Deep copy and mark as custom
        new_preset = deepcopy(source)
        new_preset['label'] = new_label
        
        self.custom_presets[new_id] = new_preset
        self.save_custom_presets()
        return {'success': True}
    
    def is_locked(self, preset_id):
        """Check if preset is locked (default preset)"""
        return preset_id in self.DEFAULT_PRESETS
