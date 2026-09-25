"""
Custom Modern UI Components for ProxyManager
Reusable styled components with sleek glassmorphism & emerald aesthetic
"""
import customtkinter as ctk
import tkinter as tk
from typing import Callable, Optional, Any, List, Tuple
from pathlib import Path
from PIL import Image

from src.ui.theme import COLORS, SPACING, RADIUS, FONTS


class ModernButton(ctk.CTkButton):
    """Modern styled button with multiple variants and states"""
    
    def __init__(
        self,
        master,
        text: str = "",
        variant: str = "primary",  # primary, secondary, danger, ghost, success, outline
        size: str = "md",          # sm, md, lg
        command: Optional[Callable] = None,
        **kwargs
    ):
        size_config = {
            'sm': {'height': 32, 'font_size': FONTS['size_sm'], 'radius': RADIUS['sm']},
            'md': {'height': 40, 'font_size': FONTS['size_md'], 'radius': RADIUS['md']},
            'lg': {'height': 48, 'font_size': FONTS['size_lg'], 'radius': RADIUS['lg']},
        }
        cfg = size_config.get(size, size_config['md'])
        
        border_width = 0
        border_color = None
        
        if variant == "primary":
            fg_color = COLORS['accent_primary']
            hover_color = COLORS['accent_hover']
            text_color = COLORS['text_inverse']
        elif variant == "secondary":
            fg_color = COLORS['bg_tertiary']
            hover_color = COLORS['bg_hover']
            text_color = COLORS['text_primary']
            border_width = 1
            border_color = COLORS['border_secondary']
        elif variant == "danger":
            fg_color = COLORS['error_bg']
            hover_color = COLORS['error']
            text_color = COLORS['text_primary']
        elif variant == "ghost":
            fg_color = "transparent"
            hover_color = COLORS['bg_hover']
            text_color = COLORS['text_secondary']
        elif variant == "success":
            fg_color = COLORS['success_bg']
            hover_color = COLORS['success']
            text_color = COLORS['text_primary']
        elif variant == "outline":
            fg_color = "transparent"
            hover_color = COLORS['bg_hover']
            text_color = COLORS['accent_primary']
            border_width = 1
            border_color = COLORS['accent_primary']
        else:
            fg_color = COLORS['accent_primary']
            hover_color = COLORS['accent_hover']
            text_color = COLORS['text_inverse']
            
        super().__init__(
            master,
            text=text,
            command=command,
            height=cfg['height'],
            font=(FONTS['family'], cfg['font_size'], FONTS['weight_medium']),
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            border_color=border_color,
            border_width=border_width,
            corner_radius=cfg['radius'],
            **kwargs
        )
        self._variant = variant

    def set_loading(self, loading: bool, loading_text: str = "Processing...") -> None:
        if loading:
            self._prev_text = self.cget("text")
            self.configure(state="disabled", text=loading_text)
        else:
            prev = getattr(self, '_prev_text', None)
            if prev:
                self.configure(state="normal", text=prev)
            else:
                self.configure(state="normal")


class IconButton(ctk.CTkButton):
    """Compact icon button"""
    
    def __init__(
        self,
        master,
        text: str = "",
        variant: str = "ghost",
        size: int = 36,
        command: Optional[Callable] = None,
        **kwargs
    ):
        if variant == "ghost":
            fg_color = "transparent"
            hover_color = COLORS['bg_hover']
            text_color = COLORS['text_secondary']
        elif variant == "primary":
            fg_color = COLORS['accent_primary']
            hover_color = COLORS['accent_hover']
            text_color = COLORS['text_inverse']
        else:
            fg_color = COLORS['bg_tertiary']
            hover_color = COLORS['bg_hover']
            text_color = COLORS['text_primary']
            
        super().__init__(
            master,
            text=text,
            command=command,
            width=size,
            height=size,
            font=(FONTS['family'], FONTS['size_md']),
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            corner_radius=RADIUS['md'],
            **kwargs
        )


class ModernCard(ctk.CTkFrame):
    """Modern styled card container with subtle border"""
    
    def __init__(
        self,
        master,
        padding: int = SPACING['md'],
        border_color: Optional[str] = None,
        fg_color: Optional[str] = None,
        border_width: int = 1,
        corner_radius: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=fg_color or COLORS['bg_card'],
            border_color=border_color or COLORS['border_primary'],
            border_width=border_width,
            corner_radius=corner_radius if corner_radius is not None else RADIUS['lg'],
            **kwargs
        )
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=0, sticky="nsew", padx=padding, pady=padding)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)


class ModernInput(ctk.CTkEntry):
    """Modern input field with active focus border"""
    
    def __init__(
        self,
        master,
        placeholder: str = "",
        show: str = None,
        **kwargs
    ):
        super().__init__(
            master,
            placeholder_text=placeholder,
            show=show,
            fg_color=COLORS['bg_secondary'],
            border_color=COLORS['border_secondary'],
            text_color=COLORS['text_primary'],
            placeholder_text_color=COLORS['text_muted'],
            corner_radius=RADIUS['md'],
            font=(FONTS['family'], FONTS['size_md']),
            height=40,
            **kwargs
        )
        self.bind("<FocusIn>", lambda e: self.configure(border_color=COLORS['border_focus']))
        self.bind("<FocusOut>", lambda e: self.configure(border_color=COLORS['border_secondary']))


class ModernLabel(ctk.CTkLabel):
    """Styled typography label"""
    
    def __init__(
        self,
        master,
        text: str = "",
        variant: str = "primary",  # primary, secondary, title, caption, success, error, warning
        **kwargs
    ):
        variants = {
            'primary': {'color': COLORS['text_primary'], 'size': FONTS['size_md'], 'weight': FONTS['weight_normal']},
            'secondary': {'color': COLORS['text_secondary'], 'size': FONTS['size_sm'], 'weight': FONTS['weight_normal']},
            'title': {'color': COLORS['text_primary'], 'size': FONTS['size_xl'], 'weight': FONTS['weight_bold']},
            'caption': {'color': COLORS['text_muted'], 'size': FONTS['size_xs'], 'weight': FONTS['weight_normal']},
            'success': {'color': COLORS['success'], 'size': FONTS['size_sm'], 'weight': FONTS['weight_medium']},
            'error': {'color': COLORS['error'], 'size': FONTS['size_sm'], 'weight': FONTS['weight_medium']},
            'warning': {'color': COLORS['warning'], 'size': FONTS['size_sm'], 'weight': FONTS['weight_medium']},
        }
        cfg = variants.get(variant, variants['primary'])
        
        super().__init__(
            master,
            text=text,
            text_color=cfg['color'],
            font=(FONTS['family'], cfg['size'], cfg['weight']),
            **kwargs
        )


class ModernSwitch(ctk.CTkSwitch):
    """Styled toggle switch"""
    
    def __init__(
        self,
        master,
        text: str = "",
        variable: Optional[tk.Variable] = None,
        command: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(
            master,
            text=text,
            variable=variable,
            command=command,
            progress_color=COLORS['accent_primary'],
            button_color=COLORS['accent_light'],
            button_hover_color=COLORS['accent_hover'],
            fg_color=COLORS['bg_tertiary'],
            font=(FONTS['family'], FONTS['size_md']),
            text_color=COLORS['text_primary'],
            **kwargs
        )


class PowerButtonWidget(ctk.CTkFrame):
    """High-res anti-aliased Power Button using generated modern artwork"""
    
    def __init__(
        self,
        master,
        command: Optional[Callable] = None,
        assets_dir: Optional[Path] = None,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.command = command
        
        if assets_dir is None:
            base = Path(__file__).parent.parent.parent / "assets"
            assets_dir = base
        self.assets_dir = assets_dir
        
        self._connected = False
        self._pulsing = False
        self._pulse_state = False
        self._pulse_job = None
        
        # Load button images
        self._img_off = self._load_image("power_off.png")
        self._img_on = self._load_image("power_on.png")
        self._img_pulse = self._load_image("power_pulse.png")
        
        # Interactive Button Image
        self.button_label = ctk.CTkLabel(
            self,
            text="",
            image=self._img_off,
            cursor="hand2"
        )
        self.button_label.pack(padx=SPACING['sm'], pady=SPACING['sm'])
        self.button_label.bind("<Button-1>", self._on_click)
        
    def _load_image(self, filename: str) -> Optional[ctk.CTkImage]:
        path = self.assets_dir / filename
        if path.exists():
            try:
                pil_img = Image.open(path)
                return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(140, 140))
            except Exception as e:
                print(f"Error loading button image {filename}: {e}")
        return None
        
    def _on_click(self, event=None):
        if self.command:
            self.command()

    def set_state(self, connected: bool, pulsing: bool = False):
        self._connected = connected
        self._pulsing = pulsing
        
        if self._pulse_job:
            self.after_cancel(self._pulse_job)
            self._pulse_job = None
            
        if connected:
            if pulsing:
                self._start_pulse()
            else:
                self.button_label.configure(image=self._img_on)
        else:
            self.button_label.configure(image=self._img_off)

    def _start_pulse(self):
        self._pulse_state = not self._pulse_state
        current_img = self._img_pulse if self._pulse_state else self._img_on
        self.button_label.configure(image=current_img)
        self._pulse_job = self.after(800, self._start_pulse)

    def set_connecting(self, connecting: bool):
        if connecting:
            self.button_label.unbind("<Button-1>")
            self.button_label.configure(cursor="watch")
            self.set_state(connected=True, pulsing=True)
        else:
            self.button_label.bind("<Button-1>", self._on_click)
            self.button_label.configure(cursor="hand2")


class ModalDialog(ctk.CTkToplevel):
    """Modern styled modal dialog"""
    
    def __init__(
        self,
        master,
        title: str = "",
        width: int = 480,
        height: int = 380,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.title("")
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        try:
            x = master.winfo_rootx() + (master.winfo_width() // 2) - (width // 2)
            y = master.winfo_rooty() + (master.winfo_height() // 2) - (height // 2)
            self.geometry(f"+{max(50, x)}+{max(50, y)}")
        except Exception:
            pass
            
        self.configure(fg_color=COLORS['bg_primary'])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Title bar
        title_bar = ctk.CTkFrame(self, fg_color=COLORS['bg_secondary'], height=50, corner_radius=0)
        title_bar.grid(row=0, column=0, sticky="ew")
        title_bar.grid_columnconfigure(0, weight=1)
        
        ModernLabel(title_bar, text=title, variant="title").grid(row=0, column=0, sticky="w", padx=SPACING['lg'], pady=SPACING['sm'])
        
        close_btn = ctk.CTkButton(
            title_bar,
            text="✕",
            width=32,
            height=32,
            fg_color="transparent",
            hover_color=COLORS['bg_hover'],
            text_color=COLORS['text_muted'],
            command=self.destroy
        )
        close_btn.grid(row=0, column=1, sticky="e", padx=SPACING['md'])
        
        # Content body
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.grid(row=1, column=0, sticky="nsew", padx=SPACING['lg'], pady=SPACING['lg'])
        self.body.grid_columnconfigure(0, weight=1)
        
        # Bind Escape key to close
        self.bind("<Escape>", lambda e: self.destroy())


class ConfirmDialog(ModalDialog):
    """Confirmation Dialog"""
    
    def __init__(
        self,
        master,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        variant: str = "danger",
        on_confirm: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(master, title, width=440, height=220, **kwargs)
        self.on_confirm = on_confirm
        
        ModernLabel(
            self.body,
            text=message,
            variant="primary",
            wraplength=380
        ).pack(anchor="w", pady=(SPACING['md'], SPACING['xl']))
        
        btn_row = ctk.CTkFrame(self.body, fg_color="transparent")
        btn_row.pack(fill="x", side="bottom")
        btn_row.grid_columnconfigure((0, 1), weight=1)
        
        ModernButton(btn_row, text=cancel_text, variant="secondary", command=self.destroy).grid(row=0, column=0, padx=(0, SPACING['sm']), sticky="ew")
        ModernButton(btn_row, text=confirm_text, variant=variant, command=self._do_confirm).grid(row=0, column=1, padx=(SPACING['sm'], 0), sticky="ew")

    def _do_confirm(self):
        if self.on_confirm:
            self.on_confirm()
        self.destroy()


class ProfileFormDialog(ModalDialog):
    """Add / Edit Profile Form with Smart URL parser & live connection tester"""
    
    def __init__(
        self,
        master,
        title: str,
        profile=None,
        on_submit: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(master, title, width=500, height=480, **kwargs)
        self.profile = profile
        self.on_submit = on_submit
        self._build_form()

    def _build_form(self):
        # Quick paste hint
        hint_label = ModernLabel(
            self.body,
            text="Tip: You can paste a full proxy (e.g. 127.0.0.1:8080) directly into Host.",
            variant="caption"
        )
        hint_label.pack(anchor="w", pady=(0, SPACING['sm']))

        # Profile Name
        ModernLabel(self.body, text="Profile Name", variant="secondary").pack(anchor="w", pady=(0, SPACING['xs']))
        self.name_entry = ModernInput(self.body, placeholder="e.g. US High-Speed / Local Clash")
        self.name_entry.pack(fill="x", pady=(0, SPACING['md']))
        if self.profile:
            self.name_entry.insert(0, self.profile.name)
            
        # Host
        ModernLabel(self.body, text="Host / IP Address", variant="secondary").pack(anchor="w", pady=(0, SPACING['xs']))
        self.host_entry = ModernInput(self.body, placeholder="e.g. 127.0.0.1 or proxy.example.com")
        self.host_entry.pack(fill="x", pady=(0, SPACING['md']))
        self.host_entry.bind("<KeyRelease>", self._auto_parse_host_port)
        if self.profile:
            self.host_entry.insert(0, self.profile.host)

        # Port
        ModernLabel(self.body, text="Port", variant="secondary").pack(anchor="w", pady=(0, SPACING['xs']))
        self.port_entry = ModernInput(self.body, placeholder="e.g. 8080, 7890, 1080")
        self.port_entry.pack(fill="x", pady=(0, SPACING['md']))
        if self.profile:
            self.port_entry.insert(0, str(self.profile.port))

        # Status / Error label
        self.status_label = ModernLabel(self.body, text="", variant="caption")
        self.status_label.pack(anchor="w", pady=(0, SPACING['md']))

        # Actions Row
        actions = ctk.CTkFrame(self.body, fg_color="transparent")
        actions.pack(fill="x", side="bottom")
        actions.grid_columnconfigure((0, 1, 2), weight=1)

        self.test_btn = ModernButton(actions, text="Test Reachability", variant="outline", size="sm", command=self._test_reachability)
        self.test_btn.grid(row=0, column=0, padx=(0, SPACING['xs']), sticky="ew")

        ModernButton(actions, text="Cancel", variant="secondary", size="sm", command=self.destroy).grid(row=0, column=1, padx=SPACING['xs'], sticky="ew")
        ModernButton(actions, text="Save Profile", variant="primary", size="sm", command=self._save).grid(row=0, column=2, padx=(SPACING['xs'], 0), sticky="ew")

    def _auto_parse_host_port(self, event=None):
        text = self.host_entry.get().strip()
        for prefix in ["http://", "https://", "socks5://", "socks4://"]:
            if text.startswith(prefix):
                text = text[len(prefix):]
                self.host_entry.delete(0, "end")
                self.host_entry.insert(0, text)
                break
        if ":" in text and not text.startswith("["):
            parts = text.split(":")
            if len(parts) == 2 and parts[1].isdigit():
                self.host_entry.delete(0, "end")
                self.host_entry.insert(0, parts[0])
                self.port_entry.delete(0, "end")
                self.port_entry.insert(0, parts[1])

    def _test_reachability(self):
        host = self.host_entry.get().strip()
        port_s = self.port_entry.get().strip()
        if not host or not port_s.isdigit():
            self.status_label.configure(text="Please enter a valid host and port first.", text_color=COLORS['warning'])
            return
        
        self.status_label.configure(text="Pinging host...", text_color=COLORS['text_secondary'])
        self.test_btn.set_loading(True, "Testing...")

        def run_test():
            import socket, time
            try:
                start = time.time()
                s = socket.create_connection((host, int(port_s)), timeout=3.0)
                s.close()
                ms = int((time.time() - start) * 1000)
                def on_ok():
                    self.test_btn.set_loading(False)
                    self.status_label.configure(text=f"✓ Reachable! Response in {ms} ms", text_color=COLORS['success'])
                self.after(0, on_ok)
            except Exception as e:
                def on_err():
                    self.test_btn.set_loading(False)
                    self.status_label.configure(text=f"✗ Unreachable: {str(e)[:35]}", text_color=COLORS['error'])
                self.after(0, on_err)

        import threading
        threading.Thread(target=run_test, daemon=True).start()

    def _save(self):
        name = self.name_entry.get().strip()
        host = self.host_entry.get().strip()
        port_s = self.port_entry.get().strip()
        
        if not name:
            self.status_label.configure(text="Profile name is required.", text_color=COLORS['error'])
            return
        if not host:
            self.status_label.configure(text="Host is required.", text_color=COLORS['error'])
            return
        try:
            port = int(port_s)
            if not (1 <= port <= 65535):
                raise ValueError()
        except ValueError:
            self.status_label.configure(text="Port must be between 1 and 65535.", text_color=COLORS['error'])
            return

        if self.on_submit:
            self.on_submit({"name": name, "host": host, "port": port})
        self.destroy()


class ProfileCard(ModernCard):
    """Modern Profile Card with status badge, ping test, and action buttons"""
    
    def __init__(
        self,
        master,
        profile,
        on_connect: Optional[Callable] = None,
        on_edit: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        is_connected: bool = False,
        is_selected: bool = False,
        **kwargs
    ):
        border_c = COLORS['accent_primary'] if is_connected else COLORS['border_primary']
        super().__init__(master, padding=SPACING['md'], border_color=border_c, **kwargs)
        self.profile = profile
        self.on_connect = on_connect
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.is_connected = is_connected
        self.is_selected = is_selected
        self._build_ui()

    def _build_ui(self):
        # 1. Top row: Name & status on left, Address & Ping on right
        top_row = ctk.CTkFrame(self.content, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, SPACING['sm']))
        
        left_header = ctk.CTkFrame(top_row, fg_color="transparent")
        left_header.pack(side="left", fill="y")
        
        # Status dot
        dot_color = COLORS['success'] if self.is_connected else (COLORS['accent_primary'] if self.is_selected else COLORS['text_muted'])
        status_dot = ctk.CTkLabel(
            left_header,
            text="●",
            text_color=dot_color,
            font=(FONTS['family'], FONTS['size_sm'])
        )
        status_dot.pack(side="left", padx=(0, SPACING['xs']))
        
        ModernLabel(left_header, text=self.profile.name, variant="title").pack(side="left")
        
        if self.is_connected:
            badge = ctk.CTkLabel(
                left_header,
                text="  CONNECTED  ",
                fg_color=COLORS['success_bg'],
                text_color=COLORS['accent_light'],
                corner_radius=RADIUS['full'],
                font=(FONTS['family'], FONTS['size_xs'], FONTS['weight_bold'])
            )
            badge.pack(side="left", padx=(SPACING['sm'], 0))
        elif self.is_selected:
            badge = ctk.CTkLabel(
                left_header,
                text="  READY  ",
                fg_color=COLORS['bg_secondary'],
                text_color=COLORS['text_secondary'],
                corner_radius=RADIUS['full'],
                font=(FONTS['family'], FONTS['size_xs'], FONTS['weight_bold'])
            )
            badge.pack(side="left", padx=(SPACING['sm'], 0))

        # Right side: Address pill + ping test
        right_header = ctk.CTkFrame(top_row, fg_color="transparent")
        right_header.pack(side="right")

        addr_badge = ctk.CTkLabel(
            right_header,
            text=f"  {self.profile.address}  ",
            fg_color=COLORS['bg_secondary'],
            text_color=COLORS['text_secondary'],
            corner_radius=RADIUS['sm'],
            font=(FONTS['family'], FONTS['size_sm'])
        )
        addr_badge.pack(side="left", padx=(0, SPACING['xs']))

        self.ping_btn = ModernButton(
            right_header,
            text="Ping",
            variant="ghost",
            size="sm",
            command=self._test_ping
        )
        self.ping_btn.pack(side="left")

        # 2. Bottom row: Connect/Disconnect on left, Edit & Delete on right
        btn_bar = ctk.CTkFrame(self.content, fg_color="transparent")
        btn_bar.pack(fill="x", pady=(SPACING['xs'], 0))

        if self.is_connected:
            connect_text = "Disconnect"
            connect_variant = "danger"
        else:
            connect_text = "Connect"
            connect_variant = "primary"
        
        ModernButton(
            btn_bar,
            text=connect_text,
            variant=connect_variant,
            size="sm",
            command=lambda: self.on_connect(self.profile, self.is_connected) if self.on_connect else None
        ).pack(side="left")

        # Right actions: Edit, Delete
        right_actions = ctk.CTkFrame(btn_bar, fg_color="transparent")
        right_actions.pack(side="right")

        ModernButton(
            right_actions,
            text="Edit",
            variant="ghost",
            size="sm",
            command=lambda: self.on_edit(self.profile) if self.on_edit else None
        ).pack(side="left", padx=(0, SPACING['xs']))

        ModernButton(
            right_actions,
            text="Delete",
            variant="danger",
            size="sm",
            command=lambda: self.on_delete(self.profile) if self.on_delete else None
        ).pack(side="left")

    def _test_ping(self):
        self.ping_btn.set_loading(True, "...")
        def run():
            import socket, time
            try:
                start = time.time()
                s = socket.create_connection((self.profile.host, self.profile.port), timeout=2.5)
                s.close()
                elapsed = int((time.time() - start) * 1000)
                def on_done():
                    self.ping_btn.set_loading(False)
                    self.ping_btn.configure(text=f"{elapsed}ms", text_color=COLORS['success'])
                self.after(0, on_done)
            except Exception:
                def on_fail():
                    self.ping_btn.set_loading(False)
                    self.ping_btn.configure(text="Offline", text_color=COLORS['error'])
                self.after(0, on_fail)
        import threading
        threading.Thread(target=run, daemon=True).start()


def show_toast(master, message: str, variant: str = "success") -> None:
    """Show an embedded in-window notification, preventing detached popups"""
    try:
        toplevel = master.winfo_toplevel()
        if hasattr(toplevel, 'notify'):
            toplevel.notify(message, variant)
            return
    except Exception:
        pass
    print(f"[{variant.upper()}] {message}")
