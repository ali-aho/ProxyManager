"""
UI Theme and Styling Constants
Modern dark glassmorphism & slate-emerald theme
"""

# Color Palette
COLORS = {
    # Background colors
    'bg_primary': '#0B0F19',      # Deep slate obsidian - main canvas
    'bg_secondary': '#111827',    # Slate 900 - sidebar / container
    'bg_tertiary': '#1E293B',     # Slate 800 - elevated surfaces
    'bg_card': '#141D2E',         # Sleek elevated card
    'bg_card_hover': '#1A263D',   # Card hover state
    'bg_hover': '#243048',        # General hover state
    
    # Border colors
    'border_primary': '#1E293B',  # Subtle card borders
    'border_secondary': '#334155', # Input & divider borders
    'border_focus': '#10B981',    # Focus borders (emerald)
    'border_subtle': '#243048',   # Very light separators
    
    # Text colors
    'text_primary': '#F8FAFC',    # Crisp white-slate text
    'text_secondary': '#94A3B8',  # Soft silver-slate secondary
    'text_muted': '#64748B',      # Muted metadata text
    'text_inverse': '#051811',    # Dark text on emerald background
    
    # Accent colors
    'accent_primary': '#10B981',  # Vibrant emerald green
    'accent_hover': '#059669',    # Emerald hover
    'accent_pressed': '#047857',  # Emerald pressed
    'accent_glow': '#34D399',     # Neon emerald glow
    'accent_light': '#6EE7B7',    # Light mint
    'accent_soft': '#064E3B',     # Deep emerald background tint
    
    # Status colors
    'success': '#10B981',         # Connected / Active
    'success_bg': '#064E3B',      # Success badge background
    'warning': '#F59E0B',         # Warning / Moderate
    'warning_bg': '#78350F',      # Warning badge background
    'error': '#EF4444',           # Error / Disconnected
    'error_bg': '#7F1D1D',        # Error badge background
    'inactive': '#64748B',        # Inactive state
    'inactive_bg': '#1E293B',      # Inactive badge background
    
    # Special
    'overlay': 'rgba(11, 15, 25, 0.85)',
    'shadow': 'rgba(0, 0, 0, 0.5)',
}

# Spacing
SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 16,
    'lg': 24,
    'xl': 32,
    'xxl': 48,
}

# Border Radius
RADIUS = {
    'sm': 6,
    'md': 10,
    'lg': 16,
    'xl': 24,
    'full': 9999,
}

# Typography
FONTS = {
    'family': 'Segoe UI',
    'size_xs': 11,
    'size_sm': 12,
    'size_md': 14,
    'size_lg': 16,
    'size_xl': 20,
    'size_2xl': 26,
    'size_3xl': 34,
    'size_4xl': 46,
    'weight_normal': 'normal',
    'weight_medium': 'bold',
    'weight_bold': 'bold',
}

# Animation durations (ms)
ANIMATION = {
    'fast': 150,
    'normal': 250,
    'slow': 350,
}


def get_color(name: str) -> str:
    """Get color by name with fallback"""
    return COLORS.get(name, '#FFFFFF')


def apply_theme(root) -> None:
    """Apply global theme to CustomTkinter root"""
    import customtkinter as ctk
    
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    root._set_appearance_mode("dark")


class ThemeManager:
    """Manages theme application across widgets"""
    
    @staticmethod
    def configure_card(widget, elevated: bool = False) -> None:
        widget.configure(
            fg_color=COLORS['bg_card'],
            border_color=COLORS['border_primary'],
            border_width=1,
            corner_radius=RADIUS['lg']
        )
    
    @staticmethod
    def configure_button_primary(widget) -> None:
        widget.configure(
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_hover'],
            text_color=COLORS['text_inverse'],
            border_width=0,
            corner_radius=RADIUS['md'],
            font=(FONTS['family'], FONTS['size_md'], FONTS['weight_medium'])
        )
    
    @staticmethod
    def configure_button_secondary(widget) -> None:
        widget.configure(
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['bg_hover'],
            text_color=COLORS['text_primary'],
            border_color=COLORS['border_primary'],
            border_width=1,
            corner_radius=RADIUS['md'],
            font=(FONTS['family'], FONTS['size_md'], FONTS['weight_normal'])
        )
    
    @staticmethod
    def configure_input(widget) -> None:
        widget.configure(
            fg_color=COLORS['bg_secondary'],
            border_color=COLORS['border_secondary'],
            text_color=COLORS['text_primary'],
            placeholder_text_color=COLORS['text_muted'],
            corner_radius=RADIUS['md'],
            font=(FONTS['family'], FONTS['size_md'])
        )
