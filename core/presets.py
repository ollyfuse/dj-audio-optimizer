import json
import os
from copy import deepcopy

class PresetManager:
    """Manages default and custom presets with validation"""
    
    DEFAULT_PRESETS = ['club_festival', 'bar_lounge', 'radio_broadcast', 'streaming_safe']
    
    # Hardcoded fallback so the app never crashes if presets.json is missing
    FALLBACK_PRESETS = {
        "club_festival": {
            "label": "Club / Festival",
            "description": "Loud, punchy, club-ready sound",
            "target_lufs": -8.0,
            "true_peak": -1.0,
            "highpass_hz": 35,
            "eq": {"low_cut_db": -2.5, "mid_cut_db": -1.8, "high_boost_db": 1.2},
            "compression": {"low": 3.0, "mid": 2.5, "high": 2.0},
            "output_format": "wav_24"
        },
        "bar_lounge": {
            "label": "Bar / Lounge",
            "description": "Smooth, controlled, conversation-friendly",
            "target_lufs": -12.0,
            "true_peak": -1.0,
            "highpass_hz": 30,
            "eq": {"low_cut_db": -1.0, "mid_cut_db": -0.5, "high_boost_db": 0.5},
            "compression": {"low": 1.8, "mid": 1.5, "high": 1.3},
            "output_format": "wav_24"
        },
        "radio_broadcast": {
            "label": "Radio / Broadcast",
            "description": "Broadcast-safe, consistent loudness",
            "target_lufs": -16.0,
            "true_peak": -1.0,
            "highpass_hz": 25,
            "eq": {"low_cut_db": -0.5, "mid_cut_db": 0.0, "high_boost_db": 0.3},
            "compression": {"low": 1.5, "mid": 1.3, "high": 1.2},
            "output_format": "wav_16"
        },
        "streaming_safe": {
            "label": "Streaming Safe",
            "description": "Spotify, Apple Music, YouTube compliant",
            "target_lufs": -14.0,
            "true_peak": -1.0,
            "highpass_hz": 28,
            "eq": {"low_cut_db": -0.8, "mid_cut_db": -0.3, "high_boost_db": 0.4},
            "compression": {"low": 1.6, "mid": 1.4, "high": 1.2},
            "output_format": "wav_16"
        }
    }
    
    def __init__(self):
        self.presets = {}
        self.custom_presets = {}
        self.config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        self.presets_file = os.path.join(self.config_dir, 'presets.json')
        self.custom_presets_file = os.path.join(self.config_dir, 'custom_presets.json')
        self.load_presets()
    
    def load_presets(self):
        """Load default and custom presets"""
        # Load default presets — fall back to hardcoded if file is missing or corrupt
        try:
            with open(self.presets_file, 'r') as f:
                self.presets = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load presets.json ({e}), using built-in defaults")
            self.presets = deepcopy(self.FALLBACK_PRESETS)
        
        # Load custom presets if file exists
        if os.path.exists(self.custom_presets_file):
            try:
                with open(self.custom_presets_file, 'r') as f:
                    self.custom_presets = json.load(f)
            except Exception:
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
        # Safe fallback — don't crash if club_festival is somehow missing
        return self.presets.get(name) or next(iter(self.presets.values()), None)
    
    def get_all_presets(self):
        """Get all presets (default + custom merged)"""
        return {**self.presets, **self.custom_presets}
    
    def get_preset_list(self):
        """Get list of presets with metadata for UI"""
        result = []
        for key, preset in self.presets.items():
            result.append({
                'id': key,
                'label': preset['label'],
                'custom': False,
                'locked': True
            })
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
        
        lufs = preset_data.get('target_lufs', -12.0)
        if lufs < -18:
            errors.append("Target LUFS too quiet (min: -18 LUFS)")
        elif lufs > -6:
            errors.append("Target LUFS too loud (max: -6 LUFS)")
        elif lufs > -7:
            warnings.append("Very aggressive LUFS - may cause distortion")
        
        peak = preset_data.get('true_peak', -1.0)
        if peak < -1.5:
            warnings.append("True peak very low - may reduce loudness")
        elif peak > -0.3:
            errors.append("True peak too high (max: -0.3 dB)")
        
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
        if preset_id in self.DEFAULT_PRESETS:
            return {'success': False, 'error': 'Cannot overwrite default preset'}
        
        validation = self.validate_preset(preset_data)
        if not validation['valid']:
            return {'success': False, 'error': validation['errors'][0]}
        
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
        
        new_preset = deepcopy(source)
        new_preset['label'] = new_label
        
        self.custom_presets[new_id] = new_preset
        self.save_custom_presets()
        return {'success': True}
    
    def is_locked(self, preset_id):
        """Check if preset is locked (default preset)"""
        return preset_id in self.DEFAULT_PRESETS
