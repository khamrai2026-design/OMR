"""
Bootstrap Theme Manager - Support for multiple professional themes.
Provides theme switching capabilities with pre-configured color palettes.
"""
from typing import Dict, Literal
from dataclasses import dataclass


@dataclass
class ThemeConfig:
    """Configuration for a theme color palette."""
    primary: str
    primary_dark: str
    secondary: str
    accent: str
    bg_glass: str
    border_glass: str
    text_main: str
    text_muted: str
    success: str
    error: str
    warning: str
    info: str
    bg_light: str
    bg_body: str


class ThemeManager:
    """
    Manager for Bootstrap multiple themes.
    Provides pre-configured themes and CSS generation.
    """

    # Premium Theme Palettes
    THEMES: Dict[str, ThemeConfig] = {
        "indigo": ThemeConfig(
            primary="#6366f1",
            primary_dark="#4f46e5",
            secondary="#ec4899",
            accent="#8b5cf6",
            bg_glass="rgba(255, 255, 255, 0.75)",
            border_glass="rgba(255, 255, 255, 0.4)",
            text_main="#0f172a",
            text_muted="#64748b",
            success="#10b981",
            error="#ef4444",
            warning="#f59e0b",
            info="#3b82f6",
            bg_light="#f8fafc",
            bg_body="radial-gradient(circle at 0% 0%, rgba(99, 102, 241, 0.03) 0%, transparent 50%), radial-gradient(circle at 100% 100%, rgba(236, 72, 153, 0.03) 0%, transparent 50%), #f8fafc"
        ),
        "ocean": ThemeConfig(
            primary="#0891b2",
            primary_dark="#0e7490",
            secondary="#06b6d4",
            accent="#00d9ff",
            bg_glass="rgba(240, 249, 255, 0.8)",
            border_glass="rgba(6, 182, 212, 0.2)",
            text_main="#082f49",
            text_muted="#164e63",
            success="#10b981",
            error="#ef4444",
            warning="#f59e0b",
            info="#0891b2",
            bg_light="#f0f9ff",
            bg_body="radial-gradient(circle at 0% 0%, rgba(8, 145, 178, 0.03) 0%, transparent 50%), radial-gradient(circle at 100% 100%, rgba(6, 182, 212, 0.03) 0%, transparent 50%), #f0f9ff"
        ),
        "forest": ThemeConfig(
            primary="#059669",
            primary_dark="#047857",
            secondary="#10b981",
            accent="#34d399",
            bg_glass="rgba(240, 253, 250, 0.8)",
            border_glass="rgba(5, 150, 105, 0.2)",
            text_main="#064e3b",
            text_muted="#065f46",
            success="#059669",
            error="#ef4444",
            warning="#f59e0b",
            info="#0891b2",
            bg_light="#f0fdf4",
            bg_body="radial-gradient(circle at 0% 0%, rgba(5, 150, 105, 0.03) 0%, transparent 50%), radial-gradient(circle at 100% 100%, rgba(16, 185, 129, 0.03) 0%, transparent 50%), #f0fdf4"
        ),
        "sunset": ThemeConfig(
            primary="#ea580c",
            primary_dark="#c2410c",
            secondary="#f97316",
            accent="#fb923c",
            bg_glass="rgba(255, 247, 237, 0.9)",
            border_glass="rgba(234, 88, 12, 0.2)",
            text_main="#7c2d12",
            text_muted="#92400e",
            success="#10b981",
            error="#ef4444",
            warning="#f59e0b",
            info="#0891b2",
            bg_light="#fffbf0",
            bg_body="radial-gradient(circle at 0% 0%, rgba(234, 88, 12, 0.03) 0%, transparent 50%), radial-gradient(circle at 100% 100%, rgba(249, 115, 22, 0.03) 0%, transparent 50%), #fffbf0"
        ),
        "violet": ThemeConfig(
            primary="#9333ea",
            primary_dark="#7e22ce",
            secondary="#a855f7",
            accent="#d946ef",
            bg_glass="rgba(250, 240, 255, 0.85)",
            border_glass="rgba(147, 51, 234, 0.2)",
            text_main="#4c0519",
            text_muted="#6b21a8",
            success="#10b981",
            error="#ef4444",
            warning="#f59e0b",
            info="#0891b2",
            bg_light="#faf5ff",
            bg_body="radial-gradient(circle at 0% 0%, rgba(147, 51, 234, 0.03) 0%, transparent 50%), radial-gradient(circle at 100% 100%, rgba(217, 70, 239, 0.03) 0%, transparent 50%), #faf5ff"
        ),
        "slate": ThemeConfig(
            primary="#64748b",
            primary_dark="#475569",
            secondary="#475569",
            accent="#78716c",
            bg_glass="rgba(248, 250, 252, 0.9)",
            border_glass="rgba(100, 116, 139, 0.2)",
            text_main="#0f172a",
            text_muted="#475569",
            success="#10b981",
            error="#ef4444",
            warning="#f59e0b",
            info="#0891b2",
            bg_light="#f8fafc",
            bg_body="radial-gradient(circle at 0% 0%, rgba(100, 116, 139, 0.03) 0%, transparent 50%), radial-gradient(circle at 100% 100%, rgba(71, 85, 105, 0.03) 0%, transparent 50%), #f8fafc"
        ),
        "rose": ThemeConfig(
            primary="#e11d48",
            primary_dark="#be185d",
            secondary="#f43f5e",
            accent="#fb7185",
            bg_glass="rgba(255, 240, 245, 0.85)",
            border_glass="rgba(225, 29, 72, 0.2)",
            text_main="#500724",
            text_muted="#831843",
            success="#10b981",
            error="#ef4444",
            warning="#f59e0b",
            info="#0891b2",
            bg_light="#fff5f7",
            bg_body="radial-gradient(circle at 0% 0%, rgba(225, 29, 72, 0.03) 0%, transparent 50%), radial-gradient(circle at 100% 100%, rgba(244, 63, 94, 0.03) 0%, transparent 50%), #fff5f7"
        ),
    }

    @staticmethod
    def get_available_themes() -> list:
        """Return list of available theme names."""
        return list(ThemeManager.THEMES.keys())

    @staticmethod
    def get_theme(theme_name: str) -> ThemeConfig:
        """
        Get theme configuration by name.
        Defaults to 'indigo' if theme not found.
        """
        return ThemeManager.THEMES.get(theme_name, ThemeManager.THEMES["indigo"])

    @staticmethod
    def get_theme_css(theme_name: str) -> str:
        """
        Generate CSS for the selected theme with modern React-style design.
        """
        theme = ThemeManager.get_theme(theme_name)

        return f"""
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
        
        <style>
        /* Modern React-Style Theme: {theme_name.title()} */
        :root {{
            --primary: {theme.primary};
            --primary-dark: {theme.primary_dark};
            --secondary: {theme.secondary};
            --accent: {theme.accent};
            --bg-glass: {theme.bg_glass};
            --border-glass: {theme.border_glass};
            --text-main: {theme.text_main};
            --text-muted: {theme.text_muted};
            --success: {theme.success};
            --error: {theme.error};
            --warning: {theme.warning};
            --info: {theme.info};
            --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
            --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.08), 0 1px 2px 0 rgba(0, 0, 0, 0.04);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 24px;
            --transition-base: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        /* Global Reset & Typography */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        .stApp {{
            background: {theme.bg_body};
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
            color: var(--text-main);
        }}

        h1 {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 3rem !important;
            font-weight: 800 !important;
            letter-spacing: -0.025em !important;
            line-height: 1.2 !important;
            color: var(--text-main) !important;
            margin-bottom: 0.5rem !important;
        }}

        h2 {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
            color: var(--text-main) !important;
            margin-bottom: 1rem !important;
        }}

        h3 {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            color: var(--text-main) !important;
            margin-bottom: 0.75rem !important;
        }}

        h4, h5, h6 {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            color: var(--text-main) !important;
        }}

        p {{
            font-family: 'Inter', sans-serif !important;
            font-size: 1rem !important;
            line-height: 1.6 !important;
            color: var(--text-muted) !important;
        }}

        /* Modern Glass Cards with Soft Shadows */
        .glass-card {{
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: var(--radius-xl);
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-md);
            transition: var(--transition-base);
            position: relative;
            overflow: hidden;
        }}

        .glass-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
        }}

        .glass-card:hover {{
            box-shadow: var(--shadow-lg);
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.5);
        }}

        .card-header-v2 {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 12px;
            letter-spacing: -0.01em;
        }}

        /* Modern Metric Cards */
        .metric-container {{
            background: white;
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            border: 1px solid rgba(0, 0, 0, 0.06);
            box-shadow: var(--shadow-sm);
            text-align: left;
            position: relative;
            overflow: hidden;
            height: 100%;
            transition: var(--transition-base);
        }}

        .metric-container::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            opacity: 0;
            transition: opacity 0.3s ease;
        }}

        .metric-container:hover {{
            border-color: var(--primary);
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }}

        .metric-container:hover::before {{
            opacity: 1;
        }}

        .metric-container::after {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100px;
            height: 100px;
            background: radial-gradient(circle, var(--primary), transparent);
            opacity: 0.05;
            border-radius: 50%;
        }}

        .metric-val {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--primary);
            margin-bottom: 0.5rem;
            line-height: 1;
            letter-spacing: -0.02em;
        }}

        .metric-lbl {{
            font-family: 'Inter', sans-serif;
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}

        /* Modern Button Styles */
        .stButton > button {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
            color: white !important;
            border-radius: var(--radius-md) !important;
            border: none !important;
            padding: 0.75rem 2rem !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            letter-spacing: 0.5px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
            transition: var(--transition-base) !important;
            width: auto !important;
            position: relative !important;
            overflow: hidden !important;
        }}

        .stButton > button::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.2);
            transition: left 0.3s ease;
        }}

        .stButton > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2) !important;
        }}

        .stButton > button:hover::before {{
            left: 100%;
        }}

        /* Input & Form Styling */
        input, textarea, select {{
            font-family: 'Inter', sans-serif !important;
            background-color: white !important;
            border: 1px solid rgba(0, 0, 0, 0.1) !important;
            border-radius: var(--radius-md) !important;
            padding: 0.75rem 1rem !important;
            font-size: 0.95rem !important;
            transition: var(--transition-base) !important;
            color: var(--text-main) !important;
        }}

        input:focus, textarea:focus, select:focus {{
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px rgba(var(--primary), 0.1) !important;
            outline: none !important;
        }}

        /* Custom Radio Toggle (Modern Style) */
        div[data-baseweb="radio"] {{
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: wrap !important;
            gap: 12px !important;
        }}

        div[data-baseweb="radio"] label {{
            background: white !important;
            border: 2px solid rgba(0, 0, 0, 0.1) !important;
            border-radius: var(--radius-md) !important;
            padding: 10px 20px !important;
            margin: 0 !important;
            transition: var(--transition-base) !important;
            box-shadow: var(--shadow-xs) !important;
            color: var(--text-muted) !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            position: relative !important;
            cursor: pointer !important;
        }}

        div[data-baseweb="radio"] label:hover {{
            border-color: var(--primary) !important;
            background: rgba(var(--primary), 0.05) !important;
            transform: translateY(-1px) !important;
        }}

        div[data-baseweb="radio"] label[data-checked="true"] {{
            background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
            color: white !important;
            border-color: var(--primary) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        }}

        /* Modern Tables */
        .modern-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
        }}

        .modern-table thead {{
            background: rgba(0, 0, 0, 0.02);
            border-bottom: 2px solid rgba(0, 0, 0, 0.08);
        }}

        .modern-table th {{
            color: var(--text-muted);
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
            padding: 1rem;
            letter-spacing: 0.05em;
            text-align: left;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }}

        .modern-table td {{
            background: white;
            padding: 1.25rem 1rem;
            font-size: 0.95rem;
            border-bottom: 1px solid rgba(0, 0, 0, 0.06);
            color: var(--text-main);
        }}

        .modern-table tbody tr:hover td {{
            background: rgba(0, 0, 0, 0.02);
        }}

        /* Status Badges (Modern Design) */
        .status-badge {{
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-family: 'Inter', sans-serif;
            backdrop-filter: blur(10px);
        }}

        .status-success {{
            background: rgba(16, 185, 129, 0.1);
            color: {theme.success};
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}

        .status-error {{
            background: rgba(239, 68, 68, 0.1);
            color: {theme.error};
            border: 1px solid rgba(239, 68, 68, 0.3);
        }}

        .status-warning {{
            background: rgba(245, 158, 11, 0.1);
            color: {theme.warning};
            border: 1px solid rgba(245, 158, 11, 0.3);
        }}

        .status-info {{
            background: rgba(59, 130, 246, 0.1);
            color: {theme.info};
            border: 1px solid rgba(59, 130, 246, 0.3);
        }}

        /* Streamlit Component Adjustments */
        .block-container {{
            padding-top: 2.5rem !important;
            max-width: 1280px !important;
        }}

        .element-container {{
            margin-bottom: 1.5rem !important;
        }}

        div[data-baseweb="select"] {{
            border-radius: var(--radius-md) !important;
        }}

        /* Modern Navbar */
        .navbar-custom {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 70px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(0, 0, 0, 0.08);
            z-index: 1000;
            display: flex;
            align-items: center;
            padding: 0 2rem;
            justify-content: space-between;
            box-shadow: var(--shadow-sm);
        }}

        .nav-logo {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-weight: 800;
            font-size: 1.5rem;
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-decoration: none;
            letter-spacing: -0.02em;
        }}

        .nav-item {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-weight: 600;
            color: var(--text-muted);
            text-decoration: none;
            transition: var(--transition-base);
            cursor: pointer;
            padding: 0.5rem 0;
            position: relative;
        }}

        .nav-item:hover, .nav-item.active {{
            color: var(--primary);
        }}

        .nav-item::after {{
            content: '';
            position: absolute;
            bottom: -5px;
            left: 0;
            width: 0;
            height: 2px;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            transition: width 0.3s ease;
        }}

        .nav-item:hover::after, .nav-item.active::after {{
            width: 100%;
        }}

        /* Main Content Adjustment */
        .main .block-container {{
            padding-top: 5rem !important;
        }}

        /* Modern Navigation Container */
        .nav-container {{
            display: flex;
            justify-content: center;
            background: rgba(255, 255, 255, 0.5);
            padding: 1rem 0;
            border-bottom: 1px solid rgba(0, 0, 0, 0.06);
            margin-bottom: 2.5rem;
            position: sticky;
            top: 70px;
            z-index: 999;
            width: 100%;
            backdrop-filter: blur(8px);
        }}

        /* Footer */
        .footer-custom {{
            margin-top: 6rem;
            padding: 4rem 2rem;
            border-top: 1px solid rgba(0, 0, 0, 0.06);
            text-align: center;
            color: var(--text-muted);
            font-size: 0.9rem;
            background: rgba(255, 255, 255, 0.3);
            backdrop-filter: blur(10px);
        }}

        /* Hide Sidebar */
        [data-testid="stSidebar"] {{
            display: none;
        }}

        /* Animations */
        @keyframes slideUp {{
            from {{
                opacity: 0;
                transform: translateY(10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes fadeIn {{
            from {{
                opacity: 0;
            }}
            to {{
                opacity: 1;
            }}
        }}

        .glass-card {{
            animation: slideUp 0.4s ease-out;
        }}

        /* Scrollbar Styling */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: rgba(0, 0, 0, 0.05);
        }}

        ::-webkit-scrollbar-thumb {{
            background: var(--primary);
            border-radius: 4px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: var(--primary-dark);
        }}

        /* Responsive Design */
        @media (max-width: 768px) {{
            h1 {{
                font-size: 2rem !important;
            }}
            
            h2 {{
                font-size: 1.5rem !important;
            }}

            .glass-card {{
                padding: 1.5rem;
            }}

            .navbar-custom {{
                padding: 0 1rem;
            }}

            .nav-logo {{
                font-size: 1.25rem;
            }}
        }}

        </style>
        """

    @staticmethod
    def get_theme_description(theme_name: str) -> str:
        """Get a friendly description of the theme."""
        descriptions = {
            "indigo": "Modern purple with pink accents - Professional & vibrant",
            "ocean": "Cool cyan & teal - Fresh & calming",
            "forest": "Rich green palette - Natural & harmonious",
            "sunset": "Warm orange & amber - Energetic & inviting",
            "violet": "Deep purple & magenta - Bold & creative",
            "slate": "Neutral gray tones - Classic & minimal",
            "rose": "Deep red & pink - Elegant & sophisticated",
        }
        return descriptions.get(theme_name, "Beautiful custom theme")
