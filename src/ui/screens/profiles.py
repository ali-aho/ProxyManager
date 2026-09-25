"""
Profiles Screen - Full proxy profile management with search, live connect and CRUD operations
"""
import customtkinter as ctk
import tkinter as tk
from typing import Optional, Callable, List
import threading

from src.ui.components import (
    ModernCard, ModernButton, ModernLabel, ModernInput,
    ProfileCard, ProfileFormDialog, ConfirmDialog, show_toast
)
from src.ui.theme import COLORS, SPACING, RADIUS, FONTS
from src.config import ProxyProfile, get_config_manager
from src.proxy_service import get_proxy_service


class ProfilesScreen(ctk.CTkFrame):
    """Profile management screen with instant connect, search and CRUD"""
    
    def __init__(
        self,
        master,
        on_profile_activated: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(master, fg_color=COLORS['bg_primary'], **kwargs)
        
        self.on_profile_activated = on_profile_activated
        self.config_manager = get_config_manager()
        self.proxy_service = get_proxy_service()
        
        self._filter_query = ""
        self._build_ui()
        self._refresh_profiles()
    
    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # 1. Header Row
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['sm']))
        header.grid_columnconfigure(0, weight=1)
        
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")
        ModernLabel(title_box, text="Profiles", variant="title").pack(side="left")
        
        self.count_badge = ctk.CTkLabel(
            title_box,
            text=" 0 ",
            fg_color=COLORS['bg_tertiary'],
            text_color=COLORS['text_muted'],
            corner_radius=RADIUS['full'],
            font=(FONTS['family'], FONTS['size_xs'], FONTS['weight_bold'])
        )
        self.count_badge.pack(side="left", padx=(SPACING['sm'], 0))
        
        ModernButton(
            header,
            text="+ Add Profile",
            variant="primary",
            size="md",
            command=self._open_add_profile
        ).grid(row=0, column=1, sticky="e")

        # 2. Search Bar
        search_bar = ctk.CTkFrame(self, fg_color="transparent")
        search_bar.grid(row=1, column=0, sticky="ew", padx=SPACING['lg'], pady=(0, SPACING['md']))
        search_bar.grid_columnconfigure(0, weight=1)
        
        self.search_input = ModernInput(search_bar, placeholder="🔍 Search profiles by name, host or port...")
        self.search_input.grid(row=0, column=0, sticky="ew")
        self.search_input.bind("<KeyRelease>", self._on_search_changed)

        # 3. Profiles Scrollable List
        self.profiles_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS['bg_tertiary'],
            scrollbar_button_hover_color=COLORS['bg_hover']
        )
        self.profiles_frame.grid(row=2, column=0, sticky="nsew", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        self.profiles_frame.grid_columnconfigure(0, weight=1)
        
        # Empty State
        self.empty_frame = ctk.CTkFrame(self.profiles_frame, fg_color="transparent")
        self.empty_frame.grid_columnconfigure(0, weight=1)
        
        ModernLabel(
            self.empty_frame,
            text="No Profiles Found",
            variant="title"
        ).pack(pady=(SPACING['xxl'], SPACING['xs']))
        
        ModernLabel(
            self.empty_frame,
            text="Add your proxy servers to switch between them seamlessly",
            variant="secondary"
        ).pack()
        
        ModernButton(
            self.empty_frame,
            text="+ Create First Profile",
            variant="primary",
            command=self._open_add_profile
        ).pack(pady=SPACING['lg'])

    def _on_search_changed(self, event=None) -> None:
        self._filter_query = self.search_input.get().strip().lower()
        self._refresh_profiles()

    def _refresh_profiles(self) -> None:
        # Clear existing cards
        for widget in self.profiles_frame.winfo_children():
            if widget != self.empty_frame:
                widget.destroy()
        
        all_profiles = self.config_manager.get_profiles()
        self.count_badge.configure(text=f" {len(all_profiles)} ")
        
        # Apply search filter
        if self._filter_query:
            profiles = [
                p for p in all_profiles
                if (self._filter_query in p.name.lower() or 
                    self._filter_query in p.host.lower() or 
                    self._filter_query in str(p.port))
            ]
        else:
            profiles = all_profiles
        
        if not profiles:
            self.empty_frame.grid(row=0, column=0, sticky="nsew")
            return
        
        self.empty_frame.grid_forget()

        # Query live system proxy state
        proxy_enabled, current_server = self.proxy_service.get_proxy_status()
        active = self.config_manager.get_active_profile()
        
        for i, profile in enumerate(profiles):
            is_selected = (active is not None and active.id == profile.id)
            is_connected = proxy_enabled and (
                is_selected or 
                current_server == profile.address or 
                current_server == f"{profile.host}:{profile.port}"
            )
            card = ProfileCard(
                self.profiles_frame,
                profile=profile,
                on_connect=self._on_connect_profile,
                on_edit=self._on_edit_profile,
                on_delete=self._on_delete_profile,
                is_connected=is_connected,
                is_selected=is_selected
            )
            card.grid(row=i, column=0, sticky="ew", pady=(0, SPACING['sm']))

    def _open_add_profile(self) -> None:
        dialog = ProfileFormDialog(
            self,
            title="Create Proxy Profile",
            on_submit=self._handle_add_profile
        )
        self.wait_window(dialog)

    def _handle_add_profile(self, data: dict) -> None:
        try:
            profile = self.config_manager.add_profile(
                name=data['name'],
                host=data['host'],
                port=data['port']
            )
            self._refresh_profiles()
            show_toast(self, f"Profile '{profile.name}' added", "success")
        except Exception as e:
            show_toast(self, f"Error creating profile: {e}", "error")

    def _on_connect_profile(self, profile: ProxyProfile, is_currently_connected: bool = False) -> None:
        if is_currently_connected:
            # Explicitly DISCONNECT
            def do_disconnect():
                ok = self.proxy_service.disable_proxy()
                def done():
                    self._refresh_profiles()
                    if ok:
                        show_toast(self, f"Disconnected from {profile.name}", "info")
                    else:
                        show_toast(self, "Failed to disconnect proxy", "error")
                    if self.on_profile_activated:
                        self.on_profile_activated(profile)
                self.after(0, done)
            threading.Thread(target=do_disconnect, daemon=True).start()
        else:
            # Explicitly CONNECT
            self.config_manager.set_active_profile(profile.id)
            def do_connect():
                ok = self.proxy_service.enable_proxy(profile.host, profile.port)
                def done():
                    self._refresh_profiles()
                    if ok:
                        show_toast(self, f"Connected to {profile.name}", "success")
                    else:
                        show_toast(self, f"Failed to enable proxy for {profile.name}", "error")
                    if self.on_profile_activated:
                        self.on_profile_activated(profile)
                self.after(0, done)
            threading.Thread(target=do_connect, daemon=True).start()

    def _on_edit_profile(self, profile: ProxyProfile) -> None:
        dialog = ProfileFormDialog(
            self,
            title=f"Edit Profile: {profile.name}",
            profile=profile,
            on_submit=lambda data: self._handle_edit_profile(profile.id, data)
        )
        self.wait_window(dialog)

    def _handle_edit_profile(self, profile_id: str, data: dict) -> None:
        success = self.config_manager.update_profile(
            profile_id=profile_id,
            name=data['name'],
            host=data['host'],
            port=data['port']
        )
        if success:
            active = self.config_manager.get_active_profile()
            if active and active.id == profile_id:
                # If currently connected profile was edited, update Windows proxy
                enabled, _ = self.proxy_service.get_proxy_status()
                if enabled:
                    self.proxy_service.enable_proxy(data['host'], data['port'])
            self._refresh_profiles()
            show_toast(self, "Profile updated", "success")
        else:
            show_toast(self, "Failed to update profile", "error")

    def _on_delete_profile(self, profile: ProxyProfile) -> None:
        dialog = ConfirmDialog(
            self,
            title="Delete Profile",
            message=f"Delete '{profile.name}' ({profile.address})?\nThis cannot be undone.",
            confirm_text="Delete",
            cancel_text="Cancel",
            variant="danger",
            on_confirm=lambda: self._handle_delete_profile(profile.id)
        )
        self.wait_window(dialog)

    def _handle_delete_profile(self, profile_id: str) -> None:
        active = self.config_manager.get_active_profile()
        if active and active.id == profile_id:
            self.proxy_service.disable_proxy()
            self.config_manager.clear_active_profile()
            
        success = self.config_manager.delete_profile(profile_id)
        if success:
            self._refresh_profiles()
            show_toast(self, "Profile deleted", "success")
        else:
            show_toast(self, "Failed to delete profile", "error")

    def refresh(self) -> None:
        self._refresh_profiles()
