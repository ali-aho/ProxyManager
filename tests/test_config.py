"""
Unit tests for Proxy Manager
"""
import unittest
import json
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config import ProxyProfile, AppSettings, ConfigManager


class TestProxyProfile(unittest.TestCase):
    """Test ProxyProfile dataclass"""
    
    def test_create_profile(self):
        profile = ProxyProfile(
            id="test123",
            name="Test Proxy",
            host="192.168.1.1",
            port=8080
        )
        self.assertEqual(profile.id, "test123")
        self.assertEqual(profile.name, "Test Proxy")
        self.assertEqual(profile.host, "192.168.1.1")
        self.assertEqual(profile.port, 8080)
        self.assertFalse(profile.is_active)
        self.assertEqual(profile.address, "192.168.1.1:8080")
    
    def test_to_dict(self):
        profile = ProxyProfile(
            id="test123",
            name="Test Proxy",
            host="192.168.1.1",
            port=8080,
            is_active=True
        )
        data = profile.to_dict()
        self.assertEqual(data['id'], "test123")
        self.assertEqual(data['name'], "Test Proxy")
        self.assertEqual(data['host'], "192.168.1.1")
        self.assertEqual(data['port'], 8080)
        self.assertTrue(data['is_active'])
    
    def test_from_dict(self):
        data = {
            'id': 'test123',
            'name': 'Test Proxy',
            'host': '192.168.1.1',
            'port': 8080,
            'is_active': True
        }
        profile = ProxyProfile.from_dict(data)
        self.assertEqual(profile.id, "test123")
        self.assertEqual(profile.name, "Test Proxy")
        self.assertEqual(profile.host, "192.168.1.1")
        self.assertEqual(profile.port, 8080)
        self.assertTrue(profile.is_active)


class TestAppSettings(unittest.TestCase):
    """Test AppSettings dataclass"""
    
    def test_default_settings(self):
        settings = AppSettings()
        self.assertFalse(settings.disable_proxy_on_startup)
        self.assertFalse(settings.run_in_tray)
        self.assertTrue(settings.minimize_to_tray)
        self.assertEqual(settings.theme, "dark")
    
    def test_custom_settings(self):
        settings = AppSettings(
            disable_proxy_on_startup=True,
            run_in_tray=True,
            minimize_to_tray=False,
            theme="light"
        )
        self.assertTrue(settings.disable_proxy_on_startup)
        self.assertTrue(settings.run_in_tray)
        self.assertFalse(settings.minimize_to_tray)
        self.assertEqual(settings.theme, "light")
    
    def test_to_dict(self):
        settings = AppSettings(disable_proxy_on_startup=True)
        data = settings.to_dict()
        self.assertTrue(data['disable_proxy_on_startup'])
    
    def test_from_dict(self):
        data = {'disable_proxy_on_startup': True, 'run_in_tray': False}
        settings = AppSettings.from_dict(data)
        self.assertTrue(settings.disable_proxy_on_startup)
        self.assertFalse(settings.run_in_tray)


class TestConfigManager(unittest.TestCase):
    """Test ConfigManager"""
    
    def setUp(self):
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.config = ConfigManager(Path(self.temp_dir))
    
    def tearDown(self):
        # Clean up temp files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initial_state(self):
        """Test initial empty state"""
        profiles = self.config.get_profiles()
        self.assertEqual(len(profiles), 0)
        
        settings = self.config.get_settings()
        self.assertIsInstance(settings, AppSettings)
    
    def test_add_profile(self):
        """Test adding a profile"""
        profile = self.config.add_profile("Test", "192.168.1.1", 8080)
        
        self.assertEqual(profile.name, "Test")
        self.assertEqual(profile.host, "192.168.1.1")
        self.assertEqual(profile.port, 8080)
        self.assertFalse(profile.is_active)
        self.assertIsNotNone(profile.id)
        
        profiles = self.config.get_profiles()
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0].name, "Test")
    
    def test_get_profile(self):
        """Test getting a specific profile"""
        profile = self.config.add_profile("Test", "192.168.1.1", 8080)
        found = self.config.get_profile(profile.id)
        
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Test")
        
        not_found = self.config.get_profile("nonexistent")
        self.assertIsNone(not_found)
    
    def test_update_profile(self):
        """Test updating a profile"""
        profile = self.config.add_profile("Test", "192.168.1.1", 8080)
        
        success = self.config.update_profile(profile.id, "Updated", "10.0.0.1", 3128)
        self.assertTrue(success)
        
        updated = self.config.get_profile(profile.id)
        self.assertEqual(updated.name, "Updated")
        self.assertEqual(updated.host, "10.0.0.1")
        self.assertEqual(updated.port, 3128)
        
        # Test updating non-existent
        success = self.config.update_profile("nonexistent", "Test", "1.1.1.1", 8080)
        self.assertFalse(success)
    
    def test_delete_profile(self):
        """Test deleting a profile"""
        profile = self.config.add_profile("Test", "192.168.1.1", 8080)
        
        success = self.config.delete_profile(profile.id)
        self.assertTrue(success)
        
        profiles = self.config.get_profiles()
        self.assertEqual(len(profiles), 0)
        
        # Test deleting non-existent
        success = self.config.delete_profile("nonexistent")
        self.assertFalse(success)
    
    def test_set_active_profile(self):
        """Test setting active profile"""
        p1 = self.config.add_profile("Profile 1", "192.168.1.1", 8080)
        p2 = self.config.add_profile("Profile 2", "10.0.0.1", 3128)
        
        # Activate first
        success = self.config.set_active_profile(p1.id)
        self.assertTrue(success)
        
        active = self.config.get_active_profile()
        self.assertEqual(active.id, p1.id)
        self.assertTrue(active.is_active)
        
        # Activate second (should deactivate first)
        success = self.config.set_active_profile(p2.id)
        self.assertTrue(success)
        
        active = self.config.get_active_profile()
        self.assertEqual(active.id, p2.id)
        self.assertTrue(active.is_active)
        
        # Check first is deactivated
        p1_check = self.config.get_profile(p1.id)
        self.assertFalse(p1_check.is_active)
        
        # Test non-existent
        success = self.config.set_active_profile("nonexistent")
        self.assertFalse(success)
    
    def test_clear_active_profile(self):
        """Test clearing active profile"""
        p1 = self.config.add_profile("Profile 1", "192.168.1.1", 8080)
        self.config.set_active_profile(p1.id)
        
        self.config.clear_active_profile()
        
        active = self.config.get_active_profile()
        self.assertIsNone(active)
        
        p1_check = self.config.get_profile(p1.id)
        self.assertFalse(p1_check.is_active)
    
    def test_settings_persistence(self):
        """Test settings are saved and loaded"""
        self.config.update_settings(disable_proxy_on_startup=True, run_in_tray=True)
        
        # Create new config manager to test loading
        config2 = ConfigManager(Path(self.temp_dir))
        settings = config2.get_settings()
        
        self.assertTrue(settings.disable_proxy_on_startup)
        self.assertTrue(settings.run_in_tray)
    
    def test_profiles_persistence(self):
        """Test profiles are saved and loaded"""
        self.config.add_profile("Test", "192.168.1.1", 8080)
        self.config.add_profile("Test2", "10.0.0.1", 3128)
        
        # Create new config manager
        config2 = ConfigManager(Path(self.temp_dir))
        profiles = config2.get_profiles()
        
        self.assertEqual(len(profiles), 2)
        names = {p.name for p in profiles}
        self.assertEqual(names, {"Test", "Test2"})
    
    def test_toggle_startup_disable(self):
        """Test toggle startup disable setting"""
        # Initial state
        settings = self.config.get_settings()
        self.assertFalse(settings.disable_proxy_on_startup)
        
        # Toggle on
        result = self.config.toggle_startup_disable()
        self.assertTrue(result)
        
        settings = self.config.get_settings()
        self.assertTrue(settings.disable_proxy_on_startup)
        
        # Toggle off
        result = self.config.toggle_startup_disable()
        self.assertFalse(result)
        
        settings = self.config.get_settings()
        self.assertFalse(settings.disable_proxy_on_startup)
    
    def test_toggle_tray(self):
        """Test toggle tray setting"""
        settings = self.config.get_settings()
        self.assertFalse(settings.run_in_tray)
        
        result = self.config.toggle_tray()
        self.assertTrue(result)
        
        settings = self.config.get_settings()
        self.assertTrue(settings.run_in_tray)


class TestConfigManagerEdgeCases(unittest.TestCase):
    """Test edge cases for ConfigManager"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_corrupted_profiles_file(self):
        """Test handling corrupted profiles.json"""
        # Write invalid JSON
        profiles_file = Path(self.temp_dir) / 'profiles.json'
        with open(profiles_file, 'w') as f:
            f.write("invalid json{")
        
        config = ConfigManager(Path(self.temp_dir))
        profiles = config.get_profiles()
        self.assertEqual(len(profiles), 0)
    
    def test_corrupted_settings_file(self):
        """Test handling corrupted settings.json"""
        settings_file = Path(self.temp_dir) / 'settings.json'
        with open(settings_file, 'w') as f:
            f.write("invalid json{")
        
        config = ConfigManager(Path(self.temp_dir))
        settings = config.get_settings()
        self.assertIsInstance(settings, AppSettings)
    
    def test_missing_files(self):
        """Test handling missing config files"""
        config = ConfigManager(Path(self.temp_dir))
        profiles = config.get_profiles()
        settings = config.get_settings()
        
        self.assertEqual(len(profiles), 0)
        self.assertIsInstance(settings, AppSettings)


if __name__ == '__main__':
    unittest.main()