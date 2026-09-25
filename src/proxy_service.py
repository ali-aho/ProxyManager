"""
Windows Proxy Service - Handles registry operations for Windows proxy settings
Uses winreg and Wininet.dll for immediate system updates
"""
import winreg
import ctypes
from ctypes import wintypes
from typing import Optional, Tuple
import sys


class ProxyService:
    """Manages Windows system proxy settings via registry and Wininet"""
    
    # Registry paths
    INTERNET_SETTINGS_KEY = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    
    # Wininet constants
    INTERNET_OPTION_REFRESH = 37
    INTERNET_OPTION_SETTINGS_CHANGED = 39
    INTERNET_OPTION_PER_CONNECTION_OPTION = 75
    
    def __init__(self):
        self._wininet = None
        self._load_wininet()
    
    def _load_wininet(self) -> None:
        """Load Wininet.dll for InternetSetOption"""
        try:
            self._wininet = ctypes.WinDLL('wininet', use_last_error=True)
            # Define function signature - HINTERNET may not be in wintypes, use c_void_p
            HINTERNET = ctypes.c_void_p
            self._wininet.InternetSetOptionW.argtypes = [
                HINTERNET,
                wintypes.DWORD,
                wintypes.LPVOID,
                wintypes.DWORD
            ]
            self._wininet.InternetSetOptionW.restype = wintypes.BOOL
        except Exception as e:
            print(f"Warning: Could not load wininet.dll: {e}")
            self._wininet = None
    
    def _notify_system_change(self) -> bool:
        """Notify Windows that proxy settings have changed"""
        if self._wininet is None:
            return False
        
        try:
            # Refresh settings
            result1 = self._wininet.InternetSetOptionW(
                None,
                self.INTERNET_OPTION_REFRESH,
                None,
                0
            )
            # Notify settings changed
            result2 = self._wininet.InternetSetOptionW(
                None,
                self.INTERNET_OPTION_SETTINGS_CHANGED,
                None,
                0
            )
            return result1 and result2
        except Exception as e:
            print(f"Error notifying system: {e}")
            return False
    
    def get_proxy_status(self) -> Tuple[bool, str]:
        """
        Get current proxy status
        Returns: (enabled: bool, proxy_server: str)
        """
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.INTERNET_SETTINGS_KEY, 0, winreg.KEY_READ) as key:
                # Get ProxyEnable
                try:
                    proxy_enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
                    enabled = bool(proxy_enable)
                except FileNotFoundError:
                    enabled = False
                
                # Get ProxyServer
                try:
                    proxy_server, _ = winreg.QueryValueEx(key, "ProxyServer")
                except FileNotFoundError:
                    proxy_server = ""
                
                return enabled, proxy_server
        except Exception as e:
            print(f"Error reading proxy status: {e}")
            return False, ""
    
    def set_proxy(self, enabled: bool, proxy_server: str = "") -> bool:
        """
        Set Windows proxy settings
        Args:
            enabled: True to enable proxy, False to disable
            proxy_server: Proxy address in format "host:port" (only used if enabled=True)
        Returns:
            True if successful
        """
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.INTERNET_SETTINGS_KEY, 0, winreg.KEY_WRITE) as key:
                # Set ProxyEnable
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1 if enabled else 0)
                
                # Set ProxyServer if enabling
                if enabled and proxy_server:
                    winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxy_server)
                elif not enabled:
                    # Clear ProxyServer when disabling
                    try:
                        winreg.DeleteValue(key, "ProxyServer")
                    except FileNotFoundError:
                        pass
            
            # Notify system of changes
            self._notify_system_change()
            return True
            
        except Exception as e:
            print(f"Error setting proxy: {e}")
            return False
    
    def enable_proxy(self, host: str, port: int) -> bool:
        """Enable proxy with specific host and port"""
        proxy_server = f"{host}:{port}"
        return self.set_proxy(True, proxy_server)
    
    def disable_proxy(self) -> bool:
        """Disable Windows proxy"""
        return self.set_proxy(False)
    
    def is_proxy_active(self) -> bool:
        """Check if proxy is currently enabled"""
        enabled, _ = self.get_proxy_status()
        return enabled
    
    def get_active_proxy_address(self) -> str:
        """Get the currently active proxy address"""
        _, proxy_server = self.get_proxy_status()
        return proxy_server
    
    def apply_startup_logic(self) -> bool:
        """
        Startup logic: If proxy is enabled, disable it silently.
        Used when app runs with --startup flag on Windows boot.
        Returns True if proxy was disabled, False if already disabled or error.
        """
        try:
            enabled, _ = self.get_proxy_status()
            if enabled:
                return self.disable_proxy()
            return False
        except Exception as e:
            print(f"Error in startup logic: {e}")
            return False


class StartupManager:
    """Manages application startup registration"""
    
    RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    APP_NAME = "ProxyManager"
    
    def __init__(self, executable_path: Optional[str] = None):
        self.executable_path = executable_path or sys.executable
    
    def is_registered(self) -> bool:
        """Check if app is registered for startup"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.RUN_KEY_PATH, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, self.APP_NAME)
                return bool(value)
        except FileNotFoundError:
            return False
        except Exception:
            return False
    
    def register(self, with_startup_flag: bool = True) -> bool:
        """Register app for Windows startup"""
        try:
            # Build command line
            if with_startup_flag:
                cmd = f'"{self.executable_path}" --startup'
            else:
                cmd = f'"{self.executable_path}"'
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.RUN_KEY_PATH, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, self.APP_NAME, 0, winreg.REG_SZ, cmd)
            return True
        except Exception as e:
            print(f"Error registering startup: {e}")
            return False
    
    def unregister(self) -> bool:
        """Unregister app from Windows startup"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.RUN_KEY_PATH, 0, winreg.KEY_WRITE) as key:
                try:
                    winreg.DeleteValue(key, self.APP_NAME)
                except FileNotFoundError:
                    pass
            return True
        except Exception as e:
            print(f"Error unregistering startup: {e}")
            return False
    
    def toggle(self, enabled: bool, with_startup_flag: bool = True) -> bool:
        """Enable or disable startup registration"""
        if enabled:
            return self.register(with_startup_flag)
        else:
            return self.unregister()


# Global instances
_proxy_service: Optional[ProxyService] = None
_startup_manager: Optional[StartupManager] = None


def get_proxy_service() -> ProxyService:
    global _proxy_service
    if _proxy_service is None:
        _proxy_service = ProxyService()
    return _proxy_service


def get_startup_manager(executable_path: Optional[str] = None) -> StartupManager:
    global _startup_manager
    if _startup_manager is None:
        _startup_manager = StartupManager(executable_path)
    return _startup_manager