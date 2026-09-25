"""
Unit tests for Proxy Service
"""
import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open, call

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from proxy_service import ProxyService, StartupManager


class TestProxyService(unittest.TestCase):
    """Test ProxyService registry operations"""
    
    def setUp(self):
        self.service = ProxyService()
    
    @patch('winreg.OpenKey')
    @patch('winreg.QueryValueEx')
    def test_get_proxy_status_enabled(self, mock_query, mock_open):
        """Test getting proxy status when enabled"""
        mock_query.side_effect = [
            (1, None),  # ProxyEnable = 1
            ("192.168.1.1:8080", None)  # ProxyServer
        ]
        
        enabled, server = self.service.get_proxy_status()
        
        self.assertTrue(enabled)
        self.assertEqual(server, "192.168.1.1:8080")
    
    @patch('winreg.OpenKey')
    @patch('winreg.QueryValueEx')
    def test_get_proxy_status_disabled(self, mock_query, mock_open):
        """Test getting proxy status when disabled"""
        mock_query.side_effect = [
            (0, None),  # ProxyEnable = 0
            ("", None)  # ProxyServer not set
        ]
        
        enabled, server = self.service.get_proxy_status()
        
        self.assertFalse(enabled)
        self.assertEqual(server, "")
    
    @patch('winreg.OpenKey')
    @patch('winreg.QueryValueEx')
    def test_get_proxy_status_missing_keys(self, mock_query, mock_open):
        """Test getting proxy status when registry keys missing"""
        import winreg
        mock_query.side_effect = FileNotFoundError()
        
        enabled, server = self.service.get_proxy_status()
        
        self.assertFalse(enabled)
        self.assertEqual(server, "")
    
    @patch('winreg.OpenKey')
    @patch('winreg.SetValueEx')
    @patch('winreg.DeleteValue')
    @patch.object(ProxyService, '_notify_system_change')
    def test_enable_proxy(self, mock_notify, mock_delete, mock_set, mock_open):
        """Test enabling proxy"""
        mock_notify.return_value = True
        
        result = self.service.enable_proxy("192.168.1.1", 8080)
        
        self.assertTrue(result)
        
        # Check SetValueEx calls
        calls = mock_set.call_args_list
        self.assertEqual(len(calls), 2)
        
        # First call: ProxyEnable = 1
        # SetValueEx(key, value_name, reserved, type, data)
        self.assertEqual(calls[0][0][1], "ProxyEnable")
        self.assertEqual(calls[0][0][4], 1)
        
        # Second call: ProxyServer = "192.168.1.1:8080"
        self.assertEqual(calls[1][0][1], "ProxyServer")
        self.assertEqual(calls[1][0][4], "192.168.1.1:8080")
        
        mock_notify.assert_called_once()
    
    @patch('winreg.OpenKey')
    @patch('winreg.SetValueEx')
    @patch('winreg.DeleteValue')
    @patch.object(ProxyService, '_notify_system_change')
    def test_disable_proxy(self, mock_notify, mock_delete, mock_set, mock_open):
        """Test disabling proxy"""
        mock_notify.return_value = True
        
        result = self.service.disable_proxy()
        
        self.assertTrue(result)
        
        # Check ProxyEnable set to 0
        mock_set.assert_called()
        call_args = mock_set.call_args
        # SetValueEx(key, value_name, reserved, type, data)
        self.assertEqual(call_args[0][1], "ProxyEnable")
        self.assertEqual(call_args[0][4], 0)
        
        # Check ProxyServer deleted
        mock_delete.assert_called()
        self.assertEqual(mock_delete.call_args[0][1], "ProxyServer")
        
        mock_notify.assert_called_once()
    
    @patch('winreg.OpenKey')
    @patch('winreg.SetValueEx')
    @patch.object(ProxyService, '_notify_system_change')
    def test_set_proxy_failure(self, mock_notify, mock_set, mock_open):
        """Test proxy set failure handling"""
        mock_set.side_effect = Exception("Registry error")
        
        result = self.service.set_proxy(True, "192.168.1.1:8080")
        
        self.assertFalse(result)
    
    @patch.object(ProxyService, 'get_proxy_status')
    @patch.object(ProxyService, 'disable_proxy')
    def test_apply_startup_logic_proxy_enabled(self, mock_disable, mock_get_status):
        """Test startup logic when proxy is enabled"""
        mock_get_status.return_value = (True, "192.168.1.1:8080")
        mock_disable.return_value = True
        
        result = self.service.apply_startup_logic()
        
        self.assertTrue(result)
        mock_disable.assert_called_once()
    
    @patch.object(ProxyService, 'get_proxy_status')
    @patch.object(ProxyService, 'disable_proxy')
    def test_apply_startup_logic_proxy_disabled(self, mock_disable, mock_get_status):
        """Test startup logic when proxy is already disabled"""
        mock_get_status.return_value = (False, "")
        
        result = self.service.apply_startup_logic()
        
        self.assertFalse(result)
        mock_disable.assert_not_called()


class TestStartupManager(unittest.TestCase):
    """Test StartupManager"""
    
    def setUp(self):
        self.manager = StartupManager("C:\\Test\\ProxyManager.exe")
    
    @patch('winreg.OpenKey')
    @patch('winreg.QueryValueEx')
    def test_is_registered_true(self, mock_query, mock_open):
        """Test is_registered when app is registered"""
        mock_query.return_value = ("C:\\Test\\ProxyManager.exe --startup", None)
        
        result = self.manager.is_registered()
        
        self.assertTrue(result)
    
    @patch('winreg.OpenKey')
    @patch('winreg.QueryValueEx')
    def test_is_registered_false(self, mock_query, mock_open):
        """Test is_registered when app is not registered"""
        import winreg
        mock_query.side_effect = FileNotFoundError()
        
        result = self.manager.is_registered()
        
        self.assertFalse(result)
    
    @patch('winreg.OpenKey')
    @patch('winreg.SetValueEx')
    def test_register(self, mock_set, mock_open):
        """Test registering for startup"""
        result = self.manager.register(with_startup_flag=True)
        
        self.assertTrue(result)
        mock_set.assert_called()
        
        # Check the command includes --startup
        # SetValueEx(key, value_name, reserved, type, data)
        call_args = mock_set.call_args
        self.assertIn("--startup", call_args[0][4])
    
    @patch('winreg.OpenKey')
    @patch('winreg.DeleteValue')
    def test_unregister(self, mock_delete, mock_open):
        """Test unregistering from startup"""
        result = self.manager.unregister()
        
        self.assertTrue(result)
        # OpenKey is used as context manager, so __enter__ returns the key
        mock_delete.assert_called_with(mock_open.return_value.__enter__.return_value, "ProxyManager")
    
    @patch('winreg.OpenKey')
    @patch('winreg.DeleteValue')
    def test_unregister_not_exists(self, mock_delete, mock_open):
        """Test unregistering when not registered"""
        import winreg
        mock_delete.side_effect = FileNotFoundError()
        
        result = self.manager.unregister()
        
        self.assertTrue(result)  # Should succeed even if not registered
    
    @patch.object(StartupManager, 'register')
    @patch.object(StartupManager, 'unregister')
    def test_toggle_enable(self, mock_unregister, mock_register):
        """Test toggle to enable"""
        mock_register.return_value = True
        
        result = self.manager.toggle(True)
        
        self.assertTrue(result)
        mock_register.assert_called_with(True)
        mock_unregister.assert_not_called()
    
    @patch.object(StartupManager, 'register')
    @patch.object(StartupManager, 'unregister')
    def test_toggle_disable(self, mock_unregister, mock_register):
        """Test toggle to disable"""
        mock_unregister.return_value = True
        
        result = self.manager.toggle(False)
        
        self.assertTrue(result)
        mock_unregister.assert_called_once()
        mock_register.assert_not_called()


if __name__ == '__main__':
    unittest.main()