# Bootstrap Multiple Themes - Documentation

## Overview

Your OMR application now supports multiple professional Bootstrap themes with seamless switching. This system allows users to choose their preferred color scheme and style from 7 carefully designed theme palettes.

## Available Themes

### 1. **Indigo** (Default)
- **Primary Color**: `#6366f1`
- **Description**: Modern purple with pink accents - Professional & vibrant
- **Best for**: Corporate environments, professional settings
- **Accent**: Purple to Violet gradient

### 2. **Ocean**
- **Primary Color**: `#0891b2`
- **Description**: Cool cyan & teal - Fresh & calming
- **Best for**: Tech companies, SaaS applications
- **Accent**: Cyan to Turquoise gradient

### 3. **Forest**
- **Primary Color**: `#059669`
- **Description**: Rich green palette - Natural & harmonious
- **Best for**: Education, environmental apps
- **Accent**: Green to Emerald gradient

### 4. **Sunset**
- **Primary Color**: `#ea580c`
- **Description**: Warm orange & amber - Energetic & inviting
- **Best for**: Creative industries, modern startups
- **Accent**: Orange to Amber gradient

### 5. **Violet**
- **Primary Color**: `#9333ea`
- **Description**: Deep purple & magenta - Bold & creative
- **Best for**: Creative platforms, design tools
- **Accent**: Purple to Magenta gradient

### 6. **Slate**
- **Primary Color**: `#64748b`
- **Description**: Neutral gray tones - Classic & minimal
- **Best for**: Minimalist designs, accessibility
- **Accent**: Gray to Dark Gray gradient

### 7. **Rose**
- **Primary Color**: `#e11d48`
- **Description**: Deep red & pink - Elegant & sophisticated
- **Best for**: Luxury brands, special occasions
- **Accent**: Rose to Pink gradient

## Architecture

### Components

#### 1. **ThemeManager** (`utils/theme_manager.py`)
Central theme management system with:
- Pre-configured theme palettes
- CSS generation for each theme
- Theme metadata and descriptions
- Easy extensibility for custom themes

#### 2. **BaseUI** (`ui/base_ui.py`)
Updated to support theme parameter:
```python
class BaseUI(ABC):
    def __init__(self, theme: str = "indigo"):
        self.theme = theme
        self.setup_styles()
```

#### 3. **UI Pages**
All UI pages now accept theme parameter:
- `ExamPageUI(theme="ocean")`
- `ResultsPageUI(theme="forest")`
- `AnalyticsPageUI(theme="violet")`

#### 4. **Main Application** (`main.py`)
Enhanced with:
- Session state management for theme persistence
- Theme selector UI component
- Dynamic page reloading on theme change

## Usage

### For Users

1. **Select Theme**: Use the theme dropdown selector in the top-right corner
2. **Auto-Save**: Your theme preference is saved in the session
3. **Instant Update**: The entire UI updates immediately with the new theme

### For Developers

#### Using a Specific Theme

```python
from ui import ExamPageUI

# Initialize with specific theme
exam_page = ExamPageUI(theme="ocean")
exam_page.render()
```

#### Getting Available Themes

```python
from utils.theme_manager import ThemeManager

# Get list of themes
themes = ThemeManager.get_available_themes()
# Output: ['indigo', 'ocean', 'forest', 'sunset', 'violet', 'slate', 'rose']
```

#### Getting Theme Configuration

```python
# Get theme config
theme_config = ThemeManager.get_theme("forest")
print(theme_config.primary)  # #059669
print(theme_config.accent)   # #34d399
```

#### Generating Theme CSS

```python
# Get CSS for a theme
css = ThemeManager.get_theme_css("sunset")
st.markdown(css, unsafe_allow_html=True)
```

#### Getting Theme Description

```python
description = ThemeManager.get_theme_description("violet")
# "Deep purple & magenta - Bold & creative"
```

## Theme Structure

Each theme consists of:

### Color Palette
- **primary**: Main brand color
- **primary_dark**: Darker variant for hover states
- **secondary**: Secondary accent color
- **accent**: Tertiary accent color
- **success**: Success state color
- **error**: Error state color
- **warning**: Warning state color
- **info**: Info state color

### Background & Glass Effects
- **bg_glass**: Glass morphism background
- **border_glass**: Glass morphism border color
- **bg_light**: Light background variant
- **bg_body**: Main page background (gradient)

### Typography
- **text_main**: Primary text color
- **text_muted**: Secondary/muted text color

## CSS Classes & Styling

All CSS is dynamically generated based on theme selection:

### Glass Cards
```html
<div class="glass-card">
    <!-- Your content -->
</div>
```

### Metric Cards
```python
self.render_metric_card("1,234", "Total Attempts")
```

### Status Badges
- `.status-success` - Green badge
- `.status-error` - Red badge
- `.status-warning` - Yellow badge
- `.status-info` - Blue badge

### Buttons
All buttons automatically use the primary theme color with gradient effect

### Tables
Modern tables with theme-aware styling via `.modern-table` class

## Extending with Custom Themes

To add a custom theme:

```python
from utils.theme_manager import ThemeManager, ThemeConfig
from dataclasses import dataclass

# Create theme config
custom_theme = ThemeConfig(
    primary="#ff6b6b",
    primary_dark="#ee5a52",
    secondary="#ff8c42",
    accent="#ff6b9d",
    bg_glass="rgba(255, 240, 245, 0.9)",
    border_glass="rgba(255, 107, 107, 0.2)",
    text_main="#2c2c2c",
    text_muted="#666666",
    success="#10b981",
    error="#ef4444",
    warning="#f59e0b",
    info="#3b82f6",
    bg_light="#fff5f7",
    bg_body="radial-gradient(...), #fff5f7"
)

# Add to themes
ThemeManager.THEMES["custom"] = custom_theme
```

## Session State Management

Theme preference is persisted using Streamlit session state:

```python
# Initialize in session
if "current_theme" not in st.session_state:
    st.session_state.current_theme = "indigo"

# Access current theme
current = st.session_state.current_theme

# Update theme
st.session_state.current_theme = "ocean"
st.rerun()  # Reload with new theme
```

## Performance Considerations

- **CSS Generation**: Done once per theme selection
- **Session State**: Persists across page interactions
- **Rerun Optimization**: Only triggered on theme change
- **No Network Overhead**: All CSS is inline

## Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support (iOS 15+)
- Bootstrap 5.3: Fully supported

## Accessibility

All themes:
- ✅ WCAG AA contrast ratios
- ✅ Support for high contrast preferences
- ✅ Clear focus states
- ✅ Readable typography across all sizes

## Future Enhancements

Potential additions:
- Dark mode variants for each theme
- User custom color picker
- Theme scheduling (auto-switch by time of day)
- Team-wide theme settings
- Export/import theme configurations
- Animation preferences per theme

## Troubleshooting

### Theme not changing?
- Clear browser cache
- Ensure `st.rerun()` is called after theme selection
- Check session state: `st.session_state.current_theme`

### Styling not applied?
- Verify CSS is being generated: Check `ThemeManager.get_theme_css()`
- Check for CSS conflicts in console
- Ensure theme name is valid

### Colors not matching?
- Verify theme exists in `ThemeManager.THEMES`
- Check hex color formats (should start with #)
- Review CSS variable names in `:root` selector

## Support

For issues or feature requests related to themes:
1. Check available themes with `ThemeManager.get_available_themes()`
2. Verify theme configuration with `ThemeManager.get_theme(theme_name)`
3. Review generated CSS with `ThemeManager.get_theme_css(theme_name)`
