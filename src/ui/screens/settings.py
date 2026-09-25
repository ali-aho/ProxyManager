"""
Settings Screen - Application preferences, system startup, tray and diagnostics
"""
import customtkinter as ctk
import tkinter as tk
import sys
import os
import webbrowser
from typing import Optional, Callable

from src.ui.components import (
    ModernCard, ModernButton, ModernLabel, ModernSwitch, show_toast
)
from src.ui.theme import COLORS, SPACING, RADIUS, FONTS
from src.config import get_config_manager
from src.proxy_service import get_startup_manager, get_proxy_service


class SettingsScreen(ctk.CTkFrame):
    """Settings screen with startup, system tray options and Windows tools"""
    
    def __init__(
        self,
        master,
        on_tray_toggle: Optional[Callable] = None,
        on_minimize: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(master, fg_color=COLORS['bg_primary'], **kwargs)
        
        self.on_tray_toggle = on_tray_toggle
        self.on_minimize = on_minimize
        self.config_manager = get_config_manager()
        self.proxy_service = get_proxy_service()
        self.startup_manager = get_startup_manager(sys.executable)
        
        self._build_ui()
        self._load_settings()
    
    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['sm']))
        ModernLabel(header, text="Settings", variant="title").pack(side="left")
        
        # Scrollable content
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS['bg_tertiary'],
            scrollbar_button_hover_color=COLORS['bg_hover']
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Sections
        self._build_startup_section()
        self._build_tray_section()
        self._build_tools_section()
        self._build_about_section()

    def _create_setting_row(
        self,
        parent,
        title: str,
        description: str,
        variable: tk.BooleanVar,
        on_toggle: Callable
    ) -> ctk.CTkFrame:
        """Create a clean modern setting row: Title + Subtitle on left, Switch on right"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=SPACING['sm'])
        row.grid_columnconfigure(0, weight=1)

        text_box = ctk.CTkFrame(row, fg_color="transparent")
        text_box.grid(row=0, column=0, sticky="w")

        ModernLabel(text_box, text=title, variant="title").pack(anchor="w")
        ModernLabel(text_box, text=description, variant="caption").pack(anchor="w", pady=(2, 0))

        switch = ModernSwitch(row, text="", variable=variable, command=on_toggle)
        switch.grid(row=0, column=1, sticky="e", padx=(SPACING['md'], 0))
        return row

    def _add_divider(self, parent) -> None:
        div = ctk.CTkFrame(parent, height=1, fg_color=COLORS['border_primary'])
        div.pack(fill="x", pady=SPACING['xs'])
    
    def _build_startup_section(self) -> None:
        """Startup configuration"""
        section = ModernCard(self.scroll_frame, padding=SPACING['lg'])
        section.pack(fill="x", pady=(0, SPACING['lg']))
        
        ModernLabel(section.content, text="Windows Startup", variant="title").pack(anchor="w", pady=(0, SPACING['sm']))
        
        # 1. Run at startup
        self.run_at_startup_var = tk.BooleanVar()
        self._create_setting_row(
            section.content,
            title="Launch ProxyManager on Windows boot",
            description="Starts ProxyManager minimized in the system tray when Windows boots.",
            variable=self.run_at_startup_var,
            on_toggle=self._on_run_at_startup_toggle
        )
        
        self._add_divider(section.content)
        
        # 2. Turn off proxy on startup
        self.startup_disable_var = tk.BooleanVar()
        self._create_setting_row(
            section.content,
            title="Turn off Windows proxy on PC startup",
            description="Guarantees any dangling Windows proxy is disabled at boot to keep connection clean.",
            variable=self.startup_disable_var,
            on_toggle=self._on_startup_disable_toggle
        )

    def _build_tray_section(self) -> None:
        """System tray configuration"""
        section = ModernCard(self.scroll_frame, padding=SPACING['lg'])
        section.pack(fill="x", pady=(0, SPACING['lg']))
        
        ModernLabel(section.content, text="System Tray & Window", variant="title").pack(anchor="w", pady=(0, SPACING['sm']))
        
        # 1. Enable tray icon
        self.tray_var = tk.BooleanVar()
        self._create_setting_row(
            section.content,
            title="Enable system tray icon",
            description="Keeps quick controls and status accessible in your Windows taskbar tray.",
            variable=self.tray_var,
            on_toggle=self._on_tray_toggle
        )
        
        self._add_divider(section.content)
        
        # 2. Minimize to tray on close
        self.minimize_tray_var = tk.BooleanVar()
        self._create_setting_row(
            section.content,
            title="Minimize to tray when closing window",
            description="Clicking the window 'X' minimizes to tray instead of quitting the application.",
            variable=self.minimize_tray_var,
            on_toggle=self._on_minimize_tray_toggle
        )

    def _build_tools_section(self) -> None:
        """Diagnostics and Windows tools"""
        section = ModernCard(self.scroll_frame, padding=SPACING['lg'])
        section.pack(fill="x", pady=(0, SPACING['lg']))
        
        ModernLabel(section.content, text="Windows Network Tools", variant="title").pack(anchor="w")
        ModernLabel(
            section.content,
            text="Quick utility actions to inspect or repair Windows proxy state.",
            variant="caption"
        ).pack(anchor="w", pady=(2, SPACING['md']))
        
        tools_row = ctk.CTkFrame(section.content, fg_color="transparent")
        tools_row.pack(fill="x")
        tools_row.grid_columnconfigure((0, 1), weight=1)
        
        ModernButton(
            tools_row,
            text="Flush Windows Proxy",
            variant="secondary",
            command=self._flush_proxy
        ).grid(row=0, column=0, padx=(0, SPACING['sm']), sticky="ew")
        
        ModernButton(
            tools_row,
            text="Open Windows Proxy Settings",
            variant="ghost",
            command=self._open_windows_settings
        ).grid(row=0, column=1, padx=(SPACING['sm'], 0), sticky="ew")

    def _build_about_section(self) -> None:
        """About and support section"""
        section = ModernCard(self.scroll_frame, padding=SPACING['lg'])
        section.pack(fill="x", pady=(0, SPACING['sm']))
        
        ModernLabel(section.content, text="ProxyManager", variant="title").pack(anchor="w")
        ModernLabel(section.content, text="Version 1.0.0 • Modern Windows Edition", variant="secondary").pack(anchor="w", pady=(2, 0))
        ModernLabel(section.content, text="Fast, lightweight proxy switcher with live latency monitoring.", variant="caption").pack(anchor="w", pady=(2, SPACING['md']))
        
        links = ctk.CTkFrame(section.content, fg_color="transparent")
        links.pack(fill="x")
        
        ModernButton(
            links,
            text="GitHub Repository",
            variant="ghost",
            size="sm",
            command=lambda: webbrowser.open("https://github.com/ali-aho/")
        ).pack(side="left", padx=(0, SPACING['md']))
        
        ModernButton(
            links,
            text="Issue Tracker",
            variant="ghost",
            size="sm",
            command=lambda: webbrowser.open("https://github.com/ali-aho/ProxyManager/issues")
        ).pack(side="left")

    def _flush_proxy(self) -> None:
        self.proxy_service.disable_proxy()
        show_toast(self, "Windows proxy flushed and disabled", "success")

    def _open_windows_settings(self) -> None:
        """Instant open Windows proxy settings without opening any cmd console"""
        try:
            os.startfile("ms-settings:network-proxy")
        except Exception:
            try:
                import subprocess
                subprocess.Popen("start ms-settings:network-proxy", shell=True, creationflags=0x08000000)
            except Exception:
                pass

    def _load_settings(self) -> None:
        settings = self.config_manager.get_settings()
        self.startup_disable_var.set(settings.disable_proxy_on_startup)
        self.run_at_startup_var.set(self.startup_manager.is_registered())
        self.tray_var.set(settings.run_in_tray)
        self.minimize_tray_var.set(settings.minimize_to_tray)
    
    def _on_startup_disable_toggle(self) -> None:
        enabled = self.startup_disable_var.get()
        self.config_manager.update_settings(disable_proxy_on_startup=enabled)
        show_toast(self, "Startup proxy disable " + ("enabled" if enabled else "disabled"), "success")
    
    def _on_run_at_startup_toggle(self) -> None:
        enabled = self.run_at_startup_var.get()
        success = self.startup_manager.toggle(enabled, with_startup_flag=True)
        if success:
            show_toast(self, "Startup launch " + ("enabled" if enabled else "disabled"), "success")
        else:
            self.run_at_startup_var.set(not enabled)
            show_toast(self, "Failed to update Windows startup setting", "error")
    
    def _on_tray_toggle(self) -> None:
        enabled = self.tray_var.get()
        self.config_manager.update_settings(run_in_tray=enabled)
        if self.on_tray_toggle:
            self.on_tray_toggle(enabled)
        show_toast(self, "System tray " + ("enabled" if enabled else "disabled"), "success")
    
    def _on_minimize_tray_toggle(self) -> None:
        enabled = self.minimize_tray_var.get()
        self.config_manager.update_settings(minimize_to_tray=enabled)
        show_toast(self, "Minimize to tray " + ("enabled" if enabled else "disabled"), "success")
    
    def refresh(self) -> None:
        self._load_settings()
