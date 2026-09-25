"""
Main Application Window - Ties together all screens with modern navigation & system tray
"""
import customtkinter as ctk
import tkinter as tk
import sys
import os
from pathlib import Path
from typing import Optional
from PIL import Image

from src.ui.screens.dashboard import DashboardScreen
from src.ui.screens.profiles import ProfilesScreen
from src.ui.screens.settings import SettingsScreen
from src.ui.components import show_toast
from src.ui.theme import COLORS, SPACING, RADIUS, FONTS, apply_theme
from src.config import get_config_manager
from src.proxy_service import get_proxy_service, get_startup_manager


class ProxyManagerApp(ctk.CTk):
    """Main application window with modern dark UI and system tray integration"""
    
    def __init__(self, startup_mode: bool = False):
        super().__init__()
        
        self.startup_mode = startup_mode
        self.config_manager = get_config_manager()
        self.proxy_service = get_proxy_service()
        self.startup_manager = get_startup_manager(sys.executable)
        
        # Base assets dir
        self.assets_dir = Path(__file__).parent.parent / "assets"
        
        # Tray state
        self._tray_icon = None
        self._tray_enabled = False
        self._minimize_to_tray = True
        
        if not startup_mode:
            self._setup_window()
            self._setup_navigation()
            self._setup_screens()
            self._apply_startup_settings()
            self._setup_tray()
            
            self.protocol("WM_DELETE_WINDOW", self._on_close)
            self.after(400, self._refresh_all)
        else:
            self.withdraw()
            self._run_startup_logic()

    def _setup_window(self) -> None:
        self.title("ProxyManager")
        self.geometry("940x660")
        self.minsize(840, 600)
        
        apply_theme(self)
        self.configure(fg_color=COLORS['bg_primary'])
        
        # Window icon
        ico_path = self.assets_dir / "icon.ico"
        if ico_path.exists():
            try:
                self.iconbitmap(default=str(ico_path))
            except Exception:
                pass
        
        # Center on screen
        self.update_idletasks()
        try:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            x = max(0, (sw - 940) // 2)
            y = max(0, (sh - 660) // 2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _setup_navigation(self) -> None:
        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            fg_color=COLORS['bg_secondary'],
            border_color=COLORS['border_primary'],
            border_width=1,
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(2, weight=1)

        # Brand / Logo Header
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="ew", padx=SPACING['lg'], pady=(SPACING['xl'], SPACING['md']))
        
        brand_row = ctk.CTkFrame(logo_frame, fg_color="transparent")
        brand_row.pack(anchor="w")
        
        # Logo Icon Image if available
        png_path = self.assets_dir / "icon.png"
        if png_path.exists():
            try:
                pil_logo = Image.open(png_path)
                logo_ctk = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(28, 28))
                logo_icon = ctk.CTkLabel(brand_row, text="", image=logo_ctk)
                logo_icon.pack(side="left", padx=(0, SPACING['sm']))
            except Exception:
                pass
                
        ctk.CTkLabel(
            brand_row,
            text="ProxyManager",
            font=(FONTS['family'], FONTS['size_xl'], FONTS['weight_bold']),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        version_pill = ctk.CTkLabel(
            logo_frame,
            text="v1.0.0 • Connected",
            font=(FONTS['family'], FONTS['size_xs']),
            text_color=COLORS['accent_light']
        )
        version_pill.pack(anchor="w", padx=(34, 0), pady=(2, 0))

        # Divider
        ctk.CTkFrame(
            self.sidebar,
            height=1,
            fg_color=COLORS['border_primary']
        ).grid(row=1, column=0, sticky="ew", padx=SPACING['md'], pady=(SPACING['xs'], SPACING['md']))

        # Navigation Buttons
        self.nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav_frame.grid(row=2, column=0, sticky="nsew", padx=SPACING['md'])
        
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "Dashboard", "⚡"),
            ("profiles", "Proxy Profiles", "🌐"),
            ("settings", "Settings", "⚙️"),
        ]
        
        for i, (sid, label, icon) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.nav_frame,
                text=f"  {icon}   {label}",
                font=(FONTS['family'], FONTS['size_md']),
                fg_color="transparent",
                text_color=COLORS['text_secondary'],
                hover_color=COLORS['bg_hover'],
                anchor="w",
                height=44,
                corner_radius=RADIUS['md'],
                command=lambda s=sid: self._switch_screen(s)
            )
            btn.grid(row=i, column=0, sticky="ew", pady=SPACING['xs'])
            self.nav_buttons[sid] = btn

        # Quick Status Card at bottom of sidebar
        bottom_status = ctk.CTkFrame(self.sidebar, fg_color=COLORS['bg_tertiary'], corner_radius=RADIUS['md'])
        bottom_status.grid(row=3, column=0, sticky="ew", padx=SPACING['md'], pady=SPACING['lg'])
        
        self.sidebar_status_lbl = ctk.CTkLabel(
            bottom_status,
            text="● System Ready",
            font=(FONTS['family'], FONTS['size_xs']),
            text_color=COLORS['accent_light']
        )
        self.sidebar_status_lbl.pack(padx=SPACING['sm'], pady=SPACING['sm'])

        self._active_screen = "dashboard"
        self._update_nav_selection()

    def _setup_screens(self) -> None:
        self.content_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_primary'], corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        self.screens = {}
        
        self.screens["dashboard"] = DashboardScreen(
            self.content_frame,
            on_profile_change=self._on_profile_changed,
            on_connect_toggle=self._on_connect_toggled
        )
        
        self.screens["profiles"] = ProfilesScreen(
            self.content_frame,
            on_profile_activated=self._on_profile_activated
        )
        
        self.screens["settings"] = SettingsScreen(
            self.content_frame,
            on_tray_toggle=self._on_tray_setting_changed,
            on_minimize=self._minimize_to_tray_action
        )

        # Embedded in-window toast notification docked at bottom-right
        self._notify_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=COLORS['bg_card'],
            border_color=COLORS['accent_primary'],
            border_width=1,
            corner_radius=RADIUS['lg']
        )
        self._notify_icon = ctk.CTkLabel(
            self._notify_frame,
            text="✓",
            text_color=COLORS['accent_light'],
            font=(FONTS['family'], FONTS['size_md'], FONTS['weight_bold'])
        )
        self._notify_icon.pack(side="left", padx=(SPACING['md'], SPACING['xs']), pady=SPACING['sm'])
        
        self._notify_label = ctk.CTkLabel(
            self._notify_frame,
            text="",
            text_color=COLORS['text_primary'],
            font=(FONTS['family'], FONTS['size_sm'])
        )
        self._notify_label.pack(side="left", padx=(0, SPACING['md']), pady=SPACING['sm'])
        
        self._notify_close = ctk.CTkButton(
            self._notify_frame,
            text="✕",
            width=20,
            height=20,
            fg_color="transparent",
            hover_color=COLORS['bg_hover'],
            text_color=COLORS['text_muted'],
            font=(FONTS['family'], FONTS['size_xs']),
            command=self._hide_notification
        )
        self._notify_close.pack(side="right", padx=(0, SPACING['sm']), pady=SPACING['sm'])
        self._notify_timer = None
        
        self._switch_screen("dashboard")

    def notify(self, message: str, variant: str = "success") -> None:
        """Display docked in-window notification banner at bottom-right"""
        if not hasattr(self, '_notify_frame'):
            return
            
        if self._notify_timer:
            self.after_cancel(self._notify_timer)
            self._notify_timer = None
            
        color_map = {
            'success': (COLORS['success_bg'], COLORS['accent_light'], "✓"),
            'error': (COLORS['error_bg'], COLORS['error'], "✕"),
            'warning': (COLORS['warning_bg'], COLORS['warning'], "⚠"),
            'info': (COLORS['bg_card'], COLORS['accent_primary'], "ℹ"),
        }
        bg, accent, icon_char = color_map.get(variant, color_map['info'])
        
        self._notify_frame.configure(fg_color=bg, border_color=accent)
        self._notify_icon.configure(text=icon_char, text_color=accent)
        self._notify_label.configure(text=message)
        
        # Place neatly at bottom-right inside content_frame
        self._notify_frame.place(relx=1.0, rely=1.0, x=-24, y=-24, anchor="se")
        self._notify_frame.lift()
        
        self._notify_timer = self.after(2600, self._hide_notification)

    def _hide_notification(self) -> None:
        if hasattr(self, '_notify_frame'):
            self._notify_frame.place_forget()
        self._notify_timer = None

    def _setup_tray(self) -> None:
        if not self._tray_enabled:
            return
            
        try:
            import pystray
            from PIL import ImageDraw
            
            def create_tray_image(connected: bool = False):
                ico_png = self.assets_dir / "icon.png"
                if ico_png.exists():
                    base = Image.open(ico_png).convert("RGBA").resize((64, 64), Image.Resampling.LANCZOS)
                else:
                    base = Image.new("RGBA", (64, 64), (15, 23, 42, 255))
                    
                draw = ImageDraw.Draw(base)
                badge_c = (16, 185, 129, 255) if connected else (100, 116, 139, 255)
                draw.ellipse([44, 44, 60, 60], fill=badge_c, outline=(255, 255, 255, 255), width=2)
                return base

            menu = pystray.Menu(
                pystray.MenuItem("Show ProxyManager", lambda: self.after(0, self._show_window), default=True),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Connect Proxy", lambda: self.after(0, self._tray_connect)),
                pystray.MenuItem("Disconnect Proxy", lambda: self.after(0, self._tray_disconnect)),
                pystray.MenuItem("Flush Windows Proxy", lambda: self.after(0, self._tray_flush)),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Quit", lambda: self.after(0, self._quit_app))
            )
            
            connected, _ = self.proxy_service.get_proxy_status()
            self._tray_icon = pystray.Icon(
                "ProxyManager",
                create_tray_image(connected),
                "ProxyManager",
                menu
            )
            
            import threading
            threading.Thread(target=self._tray_icon.run, daemon=True).start()
        except Exception as e:
            print(f"Tray setup error: {e}")

    def _tray_connect(self):
        if "dashboard" in self.screens:
            self.screens["dashboard"]._connect()

    def _tray_disconnect(self):
        if "dashboard" in self.screens:
            self.screens["dashboard"]._disconnect()

    def _tray_flush(self):
        self.proxy_service.disable_proxy()
        self._refresh_all()

    def _apply_startup_settings(self) -> None:
        settings = self.config_manager.get_settings()
        self._minimize_to_tray = settings.minimize_to_tray
        self._tray_enabled = settings.run_in_tray

    def _switch_screen(self, screen_id: str) -> None:
        if self._active_screen in self.screens:
            self.screens[self._active_screen].grid_forget()
        
        self._active_screen = screen_id
        if screen_id in self.screens:
            self.screens[screen_id].grid(row=0, column=0, sticky="nsew")
            if hasattr(self.screens[screen_id], 'refresh'):
                self.screens[screen_id].refresh()
        
        self._update_nav_selection()

    def _update_nav_selection(self) -> None:
        for screen_id, btn in self.nav_buttons.items():
            if screen_id == self._active_screen:
                btn.configure(
                    fg_color=COLORS['accent_primary'],
                    text_color=COLORS['text_inverse']
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS['text_secondary']
                )

    def _on_profile_changed(self, profile) -> None:
        if "profiles" in self.screens:
            self.screens["profiles"].refresh()
        if "dashboard" in self.screens:
            self.screens["dashboard"].refresh()

    def _on_profile_activated(self, profile) -> None:
        if "dashboard" in self.screens:
            self.screens["dashboard"].refresh()
        if "profiles" in self.screens:
            self.screens["profiles"].refresh()
        self._update_tray_icon()
        connected, _ = self.proxy_service.get_proxy_status()
        self._update_sidebar_status(connected)

    def _on_connect_toggled(self, connected: bool) -> None:
        if "profiles" in self.screens:
            self.screens["profiles"].refresh()
        self._update_tray_icon()
        self._update_sidebar_status(connected)

    def _update_sidebar_status(self, connected: bool) -> None:
        if hasattr(self, 'sidebar_status_lbl'):
            if connected:
                self.sidebar_status_lbl.configure(text="● Proxy Active", text_color=COLORS['accent_light'])
            else:
                self.sidebar_status_lbl.configure(text="○ Disconnected", text_color=COLORS['text_muted'])

    def _update_tray_icon(self) -> None:
        if not self._tray_icon:
            return
        try:
            from PIL import ImageDraw
            connected, _ = self.proxy_service.get_proxy_status()
            ico_png = self.assets_dir / "icon.png"
            if ico_png.exists():
                base = Image.open(ico_png).convert("RGBA").resize((64, 64), Image.Resampling.LANCZOS)
            else:
                base = Image.new("RGBA", (64, 64), (15, 23, 42, 255))
            draw = ImageDraw.Draw(base)
            badge_c = (16, 185, 129, 255) if connected else (100, 116, 139, 255)
            draw.ellipse([44, 44, 60, 60], fill=badge_c, outline=(255, 255, 255, 255), width=2)
            self._tray_icon.icon = base
        except Exception:
            pass

    def _on_tray_setting_changed(self, enabled: bool) -> None:
        self._tray_enabled = enabled
        if enabled:
            if not self._tray_icon:
                self._setup_tray()
        else:
            if self._tray_icon:
                try:
                    self._tray_icon.stop()
                except Exception:
                    pass
                self._tray_icon = None

    def _minimize_to_tray_action(self) -> None:
        self.withdraw()
        if self._tray_icon:
            show_toast(self, "Minimized to tray", "info")

    def _show_window(self) -> None:
        self.deiconify()
        self.lift()
        self.focus_force()

    def _on_close(self) -> None:
        if self._minimize_to_tray and self._tray_enabled:
            self.withdraw()
        else:
            self._quit_app()

    def _quit_app(self) -> None:
        if self._tray_icon:
            try:
                self._tray_icon.stop()
            except Exception:
                pass
        self.quit()
        sys.exit(0)

    def _run_startup_logic(self) -> None:
        settings = self.config_manager.get_settings()
        
        # 1. Disable proxy if setting was enabled
        if settings.disable_proxy_on_startup:
            self.proxy_service.disable_proxy()
            print("Startup: Disabled Windows proxy as configured.")

        # 2. If configured to run in tray, keep running silently
        if settings.run_in_tray:
            self._setup_window()
            self._setup_navigation()
            self._setup_screens()
            self._apply_startup_settings()
            self._setup_tray()
            self.protocol("WM_DELETE_WINDOW", self._on_close)
            self.withdraw()  # Remain hidden in tray
        else:
            # Exit
            self.after(500, self._quit_app)

    def _refresh_all(self) -> None:
        for screen in self.screens.values():
            if hasattr(screen, 'refresh'):
                screen.refresh()


def main():
    import sys
    
    # 1. Handle uninstall flag
    if "--uninstall" in sys.argv:
        try:
            get_startup_manager().unregister()
            get_proxy_service().disable_proxy()
        except Exception:
            pass
        sys.exit(0)
    
    # 2. Windows DPI Awareness
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    # 3. Single Instance Check (prevent multiple overlapping windows)
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        mutex = kernel32.CreateMutexW(None, False, "Local\\ProxyManager_App_Instance_Mutex")
        if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            print("Another instance of ProxyManager is already running.")
            sys.exit(0)
    except Exception:
        pass

    startup_mode = "--startup" in sys.argv
    app = ProxyManagerApp(startup_mode=startup_mode)
    app.mainloop()


if __name__ == "__main__":
    main()
