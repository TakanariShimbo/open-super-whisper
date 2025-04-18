import os
import json
from pathlib import Path


class Settings:
    """
    Class to handle application settings
    """
    
    def __init__(self, config_file=None):
        """
        Initialize settings
        
        Parameters:
        -----------
        config_file : str, optional
            Path to a custom config file. If not provided, the default config will be used.
        """
        # Default config path
        self.config_dir = Path(__file__).parent.parent.parent / 'config'
        self.default_config_path = self.config_dir / 'default_config.json'
        
        # User config path - store in user's home directory
        self.user_config_dir = Path.home() / 'open_super_whisper'
        self.user_config_path = self.user_config_dir / 'config.json'
        
        # Custom config path if provided
        self.custom_config_path = Path(config_file) if config_file else None
        
        # Create user config directory if it doesn't exist
        self.user_config_dir.mkdir(exist_ok=True, parents=True)
        
        # Load configurations
        self.default_config = self._load_config(self.default_config_path)
        self.user_config = self._load_config(self.user_config_path)
        self.custom_config = self._load_config(self.custom_config_path) if self.custom_config_path else {}
        
        # Merge configurations with priority: custom > user > default
        self.config = self._merge_configs()
    
    def _load_config(self, config_path):
        """Load configuration from a file"""
        if not config_path or not os.path.exists(config_path):
            return {}
            
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config from {config_path}: {e}")
            return {}
    
    def _merge_configs(self):
        """Merge configurations with priority"""
        # Start with default config
        merged = self.default_config.copy()
        
        # Update with user config
        self._recursive_update(merged, self.user_config)
        
        # Update with custom config if provided
        if self.custom_config:
            self._recursive_update(merged, self.custom_config)
            
        return merged
    
    def _recursive_update(self, d, u):
        """Recursively update dictionary d with values from dictionary u"""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._recursive_update(d[k], v)
            else:
                d[k] = v
    
    def get(self, key, default=None):
        """Get a setting value"""
        # Split the key by '.' to navigate nested dictionaries
        keys = key.split('.')
        
        # Start with the full config
        value = self.config
        
        # Navigate through the keys
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key, value):
        """Set a setting value and save to user config"""
        # Split the key by '.' to navigate nested dictionaries
        keys = key.split('.')
        
        # Start with the user config
        config = self.user_config
        
        # Navigate through the keys and create nested dictionaries if needed
        for i, k in enumerate(keys[:-1]):
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Update the merged config
        self.config = self._merge_configs()
        
        # Save to user config file
        self.save()
    
    def save(self):
        """Save the current user config to file"""
        try:
            with open(self.user_config_path, 'w') as f:
                json.dump(self.user_config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
