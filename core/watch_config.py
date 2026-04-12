import json
import os

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.json')

AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac', '.aiff', '.m4a', '.aac'}


class WatchConfig:
    """Manages watched folder configurations"""

    def __init__(self, config_path=None):
        self.config_path = config_path or _CONFIG_PATH
        self.watched_folders = []
        self.load()

    def load(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.watched_folders = data.get('watchedFolders', [])
        except Exception as e:
            print(f"Error loading watch config: {e}")
            self.watched_folders = []

    def save(self):
        try:
            config_data = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)

            config_data['watchedFolders'] = self.watched_folders

            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            print(f"Error saving watch config: {e}")

    def save_folder_snapshot(self, folder_path):
        """
        Save current state of a watched folder to disk.
        Called on app close so startup scan knows what was already there.
        Stores filename + mtime for each audio file in the folder.
        """
        try:
            snapshot = {}
            if os.path.isdir(folder_path):
                for fname in os.listdir(folder_path):
                    if os.path.splitext(fname)[1].lower() in AUDIO_EXTENSIONS:
                        fpath = os.path.join(folder_path, fname)
                        try:
                            snapshot[fname] = os.path.getmtime(fpath)
                        except Exception:
                            pass

            config_data = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)

            snapshots = config_data.get('folderSnapshots', {})
            snapshots[folder_path] = snapshot
            config_data['folderSnapshots'] = snapshots

            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)

        except Exception as e:
            print(f"Error saving folder snapshot: {e}")

    def get_folder_snapshot(self, folder_path):
        """Get last saved snapshot for a folder. Returns dict of filename: mtime"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                return data.get('folderSnapshots', {}).get(folder_path, {})
        except Exception:
            pass
        return {}

    def get_new_files_since_last_run(self, folder_path):
        """
        Compare current folder contents against last saved snapshot.
        Returns list of file paths that are new or modified since last run.
        """
        snapshot = self.get_folder_snapshot(folder_path)
        new_files = []

        if not os.path.isdir(folder_path):
            return new_files

        for fname in os.listdir(folder_path):
            if os.path.splitext(fname)[1].lower() not in AUDIO_EXTENSIONS:
                continue
            fpath = os.path.join(folder_path, fname)
            try:
                mtime = os.path.getmtime(fpath)
                # New file — not in snapshot at all
                # Modified file — mtime changed since snapshot
                if fname not in snapshot or mtime != snapshot[fname]:
                    new_files.append(fpath)
            except Exception:
                pass

        return new_files

    def add_folder(self, path, preset_id, auto_process=True, output_folder='', delete_original=False):
        for folder in self.watched_folders:
            if folder['path'] == path:
                return False
        self.watched_folders.append({
            'path': path,
            'presetId': preset_id,
            'autoProcess': auto_process,
            'outputFolder': output_folder,
            'deleteOriginal': delete_original,
            'enabled': True
        })
        self.save()
        return True

    def remove_folder(self, path):
        self.watched_folders = [f for f in self.watched_folders if f['path'] != path]
        self.save()

    def update_folder(self, path, **kwargs):
        for folder in self.watched_folders:
            if folder['path'] == path:
                folder.update(kwargs)
                self.save()
                return True
        return False

    def get_enabled_folders(self):
        return [f for f in self.watched_folders if f.get('enabled', True)]
