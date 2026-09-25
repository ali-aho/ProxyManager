"""
Configuration management for Proxy Manager
Handles profiles.json and settings.json persistence
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field


@dataclass
class ProxyProfile:
    """Represents a proxy profile configuration"""
    id: str
    name: str
    host: str
    port: int
    is_active: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProxyProfile':
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            host=data.get('host', ''),
            port=data.get('port', 0),
            is_active=data.get('is_active', False)
        )
    
    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"


@dataclass
class AppSettings:
    """Application settings"""
    disable_proxy_on_startup: bool = False
    run_in_tray: bool = False
    minimize_to_tray: bool = True
    theme: str = "dark"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppSettings':
        return cls(
            disable_proxy_on_startup=data.get('disable_proxy_on_startup', False),
            run_in_tray=data.get('run_in_tray', False),
            minimize_to_tray=data.get('minimize_to_tray', True),
            theme=data.get('theme', 'dark')
        )


class ConfigManager:
    """Manages all configuration files"""
    
    def __init__(self, app_data_dir: Optional[Path] = None):
        if app_data_dir is None:
            app_data_dir = Path(os.getenv('APPDATA', '')) / 'ProxyManager'
        self.app_data_dir = app_data_dir
        self.app_data_dir.mkdir(parents=True, exist_ok=True)
        
        self.profiles_file = self.app_data_dir / 'profiles.json'
        self.settings_file = self.app_data_dir / 'settings.json'
        
        self._profiles: List[ProxyProfile] = []
        self._settings: AppSettings = AppSettings()
        
        self.load_all()
    
    def load_all(self) -> None:
        """Load all configuration from disk"""
        self._load_profiles()
        self._load_settings()
    
    def _load_profiles(self) -> None:
        """Load profiles from JSON file"""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._profiles = [ProxyProfile.from_dict(p) for p in data]
            except (json.JSONDecodeError, KeyError):
                self._profiles = []
        else:
            self._profiles = []
            self._save_profiles()
    
    def _save_profiles(self) -> None:
        """Save profiles to JSON file"""
        try:
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump([p.to_dict() for p in self._profiles], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving profiles: {e}")
    
    def _load_settings(self) -> None:
        """Load settings from JSON file"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._settings = AppSettings.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                self._settings = AppSettings()
        else:
            self._settings = AppSettings()
            self._save_settings()
    
    def _save_settings(self) -> None:
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    # Profile operations
    def get_profiles(self) -> List[ProxyProfile]:
        return self._profiles.copy()
    
    def get_profile(self, profile_id: str) -> Optional[ProxyProfile]:
        for p in self._profiles:
            if p.id == profile_id:
                return p
        return None
    
    def get_active_profile(self) -> Optional[ProxyProfile]:
        for p in self._profiles:
            if p.is_active:
                return p
        return None
    
    def add_profile(self, name: str, host: str, port: int) -> ProxyProfile:
        import uuid
        profile = ProxyProfile(
            id=str(uuid.uuid4())[:8],
            name=name,
            host=host,
            port=port,
            is_active=False
        )
        self._profiles.append(profile)
        self._save_profiles()
        return profile
    
    def update_profile(self, profile_id: str, name: str, host: str, port: int) -> bool:
        for i, p in enumerate(self._profiles):
            if p.id == profile_id:
                self._profiles[i].name = name
                self._profiles[i].host = host
                self._profiles[i].port = port
                self._save_profiles()
                return True
        return False
    
    def delete_profile(self, profile_id: str) -> bool:
        for i, p in enumerate(self._profiles):
            if p.id == profile_id:
                self._profiles.pop(i)
                self._save_profiles()
                return True
        return False
    
    def set_active_profile(self, profile_id: str) -> bool:
        # Deactivate all
        for p in self._profiles:
            p.is_active = False
        # Activate selected
        for p in self._profiles:
            if p.id == profile_id:
                p.is_active = True
                self._save_profiles()
                return True
        return False
    
    def clear_active_profile(self) -> None:
        for p in self._profiles:
            p.is_active = False
        self._save_profiles()
    
    # Settings operations
    def get_settings(self) -> AppSettings:
        return self._settings
    
    def update_settings(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self._settings, key):
                setattr(self._settings, key, value)
        self._save_settings()
    
    def toggle_startup_disable(self) -> bool:
        self._settings.disable_proxy_on_startup = not self._settings.disable_proxy_on_startup
        self._save_settings()
        return self._settings.disable_proxy_on_startup
    
    def toggle_tray(self) -> bool:
        self._settings.run_in_tray = not self._settings.run_in_tray
        self._save_settings()
        return self._settings.run_in_tray


# Global instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(app_data_dir: Optional[Path] = None) -> ConfigManager:
    """Get or create the global config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(app_data_dir)
    return _config_manager