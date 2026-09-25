"""
Dashboard Screen - Main connect screen with hero toggle button, live stats and quick actions
"""
import customtkinter as ctk
import tkinter as tk
from typing import Optional, Callable
import threading
import time
import os

from src.ui.components import (
    ModernCard, ModernButton, ModernLabel, ModernInput,
    PowerButtonWidget, show_toast
)
from src.ui.theme import COLORS, SPACING, RADIUS, FONTS
from src.config import ProxyProfile, get_config_manager
from src.proxy_service import get_proxy_service


class DashboardScreen(ctk.CTkFrame):
    """Main dashboard screen with modern hero button, quick switcher & diagnostics"""
    
    def __init__(
        self,
        master,
        on_profile_change: Optional[Callable] = None,
        on_connect_toggle: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(master, fg_color=COLORS['bg_primary'], **kwargs)
        
        self.on_profile_change = on_profile_change
        self.on_connect_toggle = on_connect_toggle
        
        self.config_manager = get_config_manager()
        self.proxy_service = get_proxy_service()
        
        self._connected = False
        self._connected_start_time = None
        self._timer_job = None
        self._ping_check_running = False
        
        self._build_ui()
        self._refresh_status()
        self._start_periodic_sync()
    
    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        self._build_header()
        
        # Scrollable content frame
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS['bg_tertiary'],
            scrollbar_button_hover_color=COLORS['bg_hover']
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=SPACING['lg'], pady=SPACING['sm'])
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        # 1. Hero Power Button Section
        self._build_hero()
        
        # 2. Info Cards (Active Profile, Address, Latency)
        self._build_info_cards()
        
        # 3. Quick Switcher & System Tools
        self._build_quick_switcher()
        self._build_quick_actions()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent", height=56)
        header.grid(row=0, column=0, sticky="ew", padx=SPACING['lg'], pady=(SPACING['md'], 0))
        header.grid_columnconfigure(1, weight=1)
        
        # Left branding
        brand = ctk.CTkFrame(header, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="w")
        ModernLabel(brand, text="Dashboard", variant="title").pack(side="left")
        
        # Right status badge
        self.status_pill = ctk.CTkFrame(
            header,
            fg_color=COLORS['inactive_bg'],
            border_color=COLORS['border_secondary'],
            border_width=1,
            corner_radius=RADIUS['full']
        )
        self.status_pill.grid(row=0, column=2, sticky="e")
        
        self.status_dot = ctk.CTkLabel(
            self.status_pill,
            text="●",
            text_color=COLORS['inactive'],
            font=(FONTS['family'], FONTS['size_sm'])
        )
        self.status_dot.pack(side="left", padx=(SPACING['md'], SPACING['xs']), pady=SPACING['xs'])
        
        self.status_text = ModernLabel(
            self.status_pill,
            text="DISCONNECTED",
            variant="secondary"
        )
        self.status_text.pack(side="left", padx=(0, SPACING['md']), pady=SPACING['xs'])

    def _build_hero(self) -> None:
        hero_card = ModernCard(self.scroll_frame, padding=SPACING['xl'])
        hero_card.grid(row=0, column=0, sticky="ew", pady=(0, SPACING['lg']))
        hero_card.grid_columnconfigure(0, weight=1)
        
        center_frame = ctk.CTkFrame(hero_card.content, fg_color="transparent")
        center_frame.grid(row=0, column=0)
        
        # Modern Power Button Component
        self.power_widget = PowerButtonWidget(
            center_frame,
            command=self._on_power_click
        )
        self.power_widget.pack(pady=(0, SPACING['sm']))
        
        # Status headline
        self.hero_status_label = ModernLabel(
            center_frame,
            text="Tap to Connect",
            variant="title"
        )
        self.hero_status_label.pack(pady=(SPACING['xs'], 0))
        
        # Sub-status / Duration
        self.hero_sub_label = ModernLabel(
            center_frame,
            text="Select a proxy profile to secure Windows traffic",
            variant="secondary"
        )
        self.hero_sub_label.pack(pady=(SPACING['xs'], 0))

    def _build_info_cards(self) -> None:
        cards_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, SPACING['lg']))
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Card 1: Active Profile
        self.profile_card = ModernCard(cards_frame, padding=SPACING['md'])
        self.profile_card.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING['xs']))
        ModernLabel(self.profile_card.content, text="ACTIVE PROFILE", variant="caption").pack(anchor="w")
        self.profile_name_label = ModernLabel(self.profile_card.content, text="None", variant="title")
        self.profile_name_label.pack(anchor="w", pady=(SPACING['xs'], 0))
        
        # Card 2: Proxy Address with Copy
        self.address_card = ModernCard(cards_frame, padding=SPACING['md'])
        self.address_card.grid(row=0, column=1, sticky="nsew", padx=SPACING['xs'])
        
        addr_header = ctk.CTkFrame(self.address_card.content, fg_color="transparent")
        addr_header.pack(fill="x")
        ModernLabel(addr_header, text="SYSTEM PROXY", variant="caption").pack(side="left")
        
        self.copy_btn = ModernButton(
            addr_header,
            text="Copy",
            variant="ghost",
            size="sm",
            command=self._copy_address
        )
        self.copy_btn.pack(side="right")
        
        self.address_label = ModernLabel(self.address_card.content, text="—", variant="title")
        self.address_label.pack(anchor="w", pady=(SPACING['xs'], 0))
        
        # Card 3: Latency
        self.ping_card = ModernCard(cards_frame, padding=SPACING['md'])
        self.ping_card.grid(row=0, column=2, sticky="nsew", padx=(SPACING['xs'], 0))
        
        ping_header = ctk.CTkFrame(self.ping_card.content, fg_color="transparent")
        ping_header.pack(fill="x")
        ModernLabel(ping_header, text="LATENCY", variant="caption").pack(side="left")
        
        self.ping_btn = ModernButton(
            ping_header,
            text="Ping",
            variant="ghost",
            size="sm",
            command=self._test_ping
        )
        self.ping_btn.pack(side="right")
        
        self.ping_label = ModernLabel(self.ping_card.content, text="—", variant="title")
        self.ping_label.pack(anchor="w", pady=(SPACING['xs'], 0))

    def _build_quick_switcher(self) -> None:
        switcher_card = ModernCard(self.scroll_frame, padding=SPACING['md'])
        switcher_card.grid(row=2, column=0, sticky="ew", pady=(0, SPACING['lg']))
        
        row_frame = ctk.CTkFrame(switcher_card.content, fg_color="transparent")
        row_frame.pack(fill="x")
        row_frame.grid_columnconfigure(1, weight=1)
        
        title_box = ctk.CTkFrame(row_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")
        ModernLabel(title_box, text="Quick Profile Switch", variant="primary").pack(anchor="w")
        ModernLabel(title_box, text="Change current proxy destination instantly", variant="caption").pack(anchor="w")
        
        # Option Menu
        self.profile_var = tk.StringVar()
        profiles = self.config_manager.get_profiles()
        profile_names = [p.name for p in profiles]
        
        if profile_names:
            active = self.config_manager.get_active_profile()
            self.profile_var.set(active.name if active else profile_names[0])
            
        self.profile_dropdown = ctk.CTkOptionMenu(
            row_frame,
            variable=self.profile_var,
            values=profile_names if profile_names else ["No profiles"],
            fg_color=COLORS['bg_secondary'],
            button_color=COLORS['accent_primary'],
            button_hover_color=COLORS['accent_hover'],
            text_color=COLORS['text_primary'],
            dropdown_fg_color=COLORS['bg_card'],
            dropdown_text_color=COLORS['text_primary'],
            dropdown_hover_color=COLORS['bg_hover'],
            corner_radius=RADIUS['md'],
            font=(FONTS['family'], FONTS['size_md']),
            command=self._on_dropdown_select
        )
        self.profile_dropdown.grid(row=0, column=1, sticky="e")
        if not profile_names:
            self.profile_dropdown.configure(state="disabled")

    def _build_quick_actions(self) -> None:
        actions_card = ModernCard(self.scroll_frame, padding=SPACING['md'])
        actions_card.grid(row=3, column=0, sticky="ew", pady=(0, SPACING['md']))
        
        row = ctk.CTkFrame(actions_card.content, fg_color="transparent")
        row.pack(fill="x")
        row.grid_columnconfigure((0, 1), weight=1)
        
        # Emergency Reset Windows Proxy
        ModernButton(
            row,
            text="Flush Windows Proxy",
            variant="secondary",
            command=self._emergency_flush
        ).grid(row=0, column=0, padx=(0, SPACING['sm']), sticky="ew")
        
        # Open Windows Settings
        ModernButton(
            row,
            text="Windows Proxy Settings",
            variant="ghost",
            command=self._open_windows_settings
        ).grid(row=0, column=1, padx=(SPACING['sm'], 0), sticky="ew")

    def _on_power_click(self) -> None:
        if self._connected:
            self._disconnect()
        else:
            self._connect()

    def _connect(self) -> None:
        active_profile = self.config_manager.get_active_profile()
        if not active_profile:
            profiles = self.config_manager.get_profiles()
            if profiles:
                active_profile = profiles[0]
                self.config_manager.set_active_profile(active_profile.id)
            else:
                show_toast(self, "No profiles available. Create one first!", "error")
                return

        self.power_widget.set_connecting(True)
        self.hero_status_label.configure(text="Connecting...")
        self.hero_sub_label.configure(text=f"Routing traffic via {active_profile.address}")

        def do_enable():
            ok = self.proxy_service.enable_proxy(active_profile.host, active_profile.port)
            def done():
                self.power_widget.set_connecting(False)
                if ok:
                    self._set_connected_state(True)
                    show_toast(self, f"Connected to {active_profile.name}", "success")
                    if self.on_connect_toggle:
                        self.on_connect_toggle(True)
                else:
                    self._set_connected_state(False)
                    show_toast(self, "Failed to enable Windows proxy", "error")
            self.after(0, done)

        threading.Thread(target=do_enable, daemon=True).start()

    def _disconnect(self) -> None:
        self.power_widget.set_connecting(True)
        self.hero_status_label.configure(text="Disconnecting...")

        def do_disable():
            ok = self.proxy_service.disable_proxy()
            def done():
                self.power_widget.set_connecting(False)
                if ok:
                    self._set_connected_state(False)
                    show_toast(self, "Windows proxy disconnected", "success")
                    if self.on_connect_toggle:
                        self.on_connect_toggle(False)
                else:
                    show_toast(self, "Failed to disable proxy", "error")
            self.after(0, done)

        threading.Thread(target=do_disable, daemon=True).start()

    def _set_connected_state(self, connected: bool) -> None:
        self._connected = connected
        self.power_widget.set_state(connected)

        if connected:
            self._connected_start_time = time.time()
            self._start_timer()
            
            self.status_pill.configure(fg_color=COLORS['success_bg'], border_color=COLORS['accent_primary'])
            self.status_dot.configure(text_color=COLORS['accent_light'])
            self.status_text.configure(text="CONNECTED", text_color=COLORS['accent_light'])
            
            active = self.config_manager.get_active_profile()
            name = active.name if active else "Proxy"
            self.hero_status_label.configure(text=f"Secured with {name}")
        else:
            self._stop_timer()
            self._connected_start_time = None
            
            self.status_pill.configure(fg_color=COLORS['inactive_bg'], border_color=COLORS['border_secondary'])
            self.status_dot.configure(text_color=COLORS['inactive'])
            self.status_text.configure(text="DISCONNECTED", text_color=COLORS['text_secondary'])
            
            self.hero_status_label.configure(text="Tap to Connect")
            self.hero_sub_label.configure(text="Select a proxy profile to secure Windows traffic")

        self._refresh_info_cards()

    def _start_timer(self) -> None:
        self._stop_timer()
        def update():
            if self._connected and self._connected_start_time:
                elapsed = int(time.time() - self._connected_start_time)
                h = elapsed // 3600
                m = (elapsed % 3600) // 60
                s = elapsed % 60
                self.hero_sub_label.configure(text=f"Active duration: {h:02d}:{m:02d}:{s:02d}")
                self._timer_job = self.after(1000, update)
        update()

    def _stop_timer(self) -> None:
        if self._timer_job:
            self.after_cancel(self._timer_job)
            self._timer_job = None

    def _on_dropdown_select(self, name: str) -> None:
        profiles = self.config_manager.get_profiles()
        for p in profiles:
            if p.name == name:
                self.config_manager.set_active_profile(p.id)
                self._refresh_info_cards()
                if self._connected:
                    # Switch proxy server live
                    self.proxy_service.enable_proxy(p.host, p.port)
                    show_toast(self, f"Switched to {p.name}", "success")
                else:
                    show_toast(self, f"Selected profile: {p.name}", "info")
                if self.on_profile_change:
                    self.on_profile_change(p)
                break

    def _refresh_info_cards(self) -> None:
        active = self.config_manager.get_active_profile()
        if active:
            self.profile_name_label.configure(text=active.name)
            self.address_label.configure(text=active.address)
        else:
            self.profile_name_label.configure(text="None")
            self.address_label.configure(text="—")

        # Sync dropdown list
        profiles = self.config_manager.get_profiles()
        names = [p.name for p in profiles]
        self.profile_dropdown.configure(values=names if names else ["No profiles"])
        if names:
            self.profile_dropdown.configure(state="normal")
            if active:
                self.profile_var.set(active.name)
        else:
            self.profile_dropdown.configure(state="disabled")

    def _copy_address(self) -> None:
        active = self.config_manager.get_active_profile()
        if active:
            self.clipboard_clear()
            self.clipboard_append(active.address)
            show_toast(self, f"Copied {active.address} to clipboard", "success")
        else:
            show_toast(self, "No address to copy", "info")

    def _test_ping(self) -> None:
        if self._ping_check_running:
            return
        active = self.config_manager.get_active_profile()
        if not active:
            show_toast(self, "No active profile to ping", "error")
            return

        self._ping_check_running = True
        self.ping_btn.set_loading(True, "...")
        self.ping_label.configure(text="...")

        def do_ping():
            import socket, time
            try:
                start = time.time()
                s = socket.create_connection((active.host, active.port), timeout=3.0)
                s.close()
                ms = int((time.time() - start) * 1000)
                def done():
                    self._ping_check_running = False
                    self.ping_btn.set_loading(False)
                    self.ping_label.configure(text=f"{ms} ms")
                    if ms < 80:
                        self.ping_label.configure(text_color=COLORS['success'])
                    elif ms < 200:
                        self.ping_label.configure(text_color=COLORS['warning'])
                    else:
                        self.ping_label.configure(text_color=COLORS['error'])
                self.after(0, done)
            except Exception:
                def fail():
                    self._ping_check_running = False
                    self.ping_btn.set_loading(False)
                    self.ping_label.configure(text="Offline", text_color=COLORS['error'])
                self.after(0, fail)

        threading.Thread(target=do_ping, daemon=True).start()

    def _emergency_flush(self) -> None:
        """Emergency reset Windows proxy settings to OFF"""
        ok = self.proxy_service.disable_proxy()
        self._set_connected_state(False)
        if ok:
            show_toast(self, "Windows proxy flushed & disabled", "success")
        else:
            show_toast(self, "Proxy already disabled", "info")

    def _open_windows_settings(self) -> None:
        """Open Windows network proxy settings directly without cmd window"""
        try:
            os.startfile("ms-settings:network-proxy")
        except Exception:
            try:
                import subprocess
                subprocess.Popen("start ms-settings:network-proxy", shell=True, creationflags=0x08000000)
            except Exception:
                pass

    def _refresh_status(self) -> None:
        enabled, proxy_server = self.proxy_service.get_proxy_status()
        if enabled and proxy_server:
            if not self._connected:
                self._set_connected_state(True)
        else:
            if self._connected:
                self._set_connected_state(False)

    def _start_periodic_sync(self) -> None:
        """Check system proxy state in background periodically"""
        def sync_loop():
            self._refresh_status()
            self.after(3000, self._start_periodic_sync)
        self.after(3000, sync_loop)

    def refresh(self) -> None:
        self._refresh_status()
        self._refresh_info_cards()
