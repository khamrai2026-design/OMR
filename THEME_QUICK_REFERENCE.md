# Theme System - Quick Reference

## 🎨 Available Themes

```
indigo  → Purple + Pink (Default)
ocean   → Cyan + Teal
forest  → Green + Emerald
sunset  → Orange + Amber
violet  → Purple + Magenta
slate   → Gray + Charcoal
rose    → Red + Pink
```

## 🚀 Quick Start

### Run the app with themes:
```bash
streamlit run main.py
```

### Select theme:
- Look for the "Select Theme:" dropdown in the top-right
- Choose from 7 professional themes
- Instant UI update!

## 💻 Developer Usage

### Get all themes:
```python
from utils.theme_manager import ThemeManager

themes = ThemeManager.get_available_themes()
```

### Use specific theme:
```python
from ui import ExamPageUI

page = ExamPageUI(theme="ocean")
page.render()
```

### Get theme info:
```python
config = ThemeManager.get_theme("forest")
print(config.primary)    # #059669
print(config.success)    # #10b981
```

### Get theme description:
```python
desc = ThemeManager.get_theme_description("violet")
# "Deep purple & magenta - Bold & creative"
```

## 📊 Theme Colors Reference

### Indigo (Default)
```
Primary:     #6366f1
Primary Dk:  #4f46e5
Secondary:   #ec4899
Accent:      #8b5cf6
Success:     #10b981
Error:       #ef4444
```

### Ocean
```
Primary:     #0891b2
Primary Dk:  #0e7490
Secondary:   #06b6d4
Accent:      #00d9ff
Success:     #10b981
Error:       #ef4444
```

### Forest
```
Primary:     #059669
Primary Dk:  #047857
Secondary:   #10b981
Accent:      #34d399
Success:     #059669
Error:       #ef4444
```

### Sunset
```
Primary:     #ea580c
Primary Dk:  #c2410c
Secondary:   #f97316
Accent:      #fb923c
Success:     #10b981
Error:       #ef4444
```

### Violet
```
Primary:     #9333ea
Primary Dk:  #7e22ce
Secondary:   #a855f7
Accent:      #d946ef
Success:     #10b981
Error:       #ef4444
```

### Slate
```
Primary:     #64748b
Primary Dk:  #475569
Secondary:   #475569
Accent:      #78716c
Success:     #10b981
Error:       #ef4444
```

### Rose
```
Primary:     #e11d48
Primary Dk:  #be185d
Secondary:   #f43f5e
Accent:      #fb7185
Success:     #10b981
Error:       #ef4444
```

## 🔧 Add Custom Theme

```python
from utils.theme_manager import ThemeManager, ThemeConfig

# Create theme
my_theme = ThemeConfig(
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

# Add to manager
ThemeManager.THEMES["my_custom"] = my_theme
```

## 📁 Files Modified/Created

### Created:
- ✅ `utils/theme_manager.py` - Theme manager system

### Modified:
- ✅ `ui/base_ui.py` - Theme support
- ✅ `ui/exam_page.py` - Theme parameter
- ✅ `ui/results_page.py` - Theme parameter
- ✅ `ui/analytics_page.py` - Theme parameter
- ✅ `main.py` - Theme selector & persistence
- ✅ `utils/__init__.py` - Export ThemeManager

## 📚 Documentation Files

- 📄 `THEMES.md` - Full theme documentation
- 📄 `THEME_IMPLEMENTATION.md` - Implementation guide
- 📄 `THEME_QUICK_REFERENCE.md` - This file

## ✨ Features

✅ 7 Professional themes
✅ Instant switching
✅ Session persistence
✅ WCAG AA compliant
✅ No breaking changes
✅ Easy customization
✅ Dynamic CSS generation

## 🎯 How It Works

1. User selects theme from dropdown
2. Session state updates
3. App reruns with new theme
4. CSS regenerated for selected theme
5. UI updates instantly

## 💡 Tips

- **Default theme**: Indigo (modern & professional)
- **For calming feel**: Ocean or Forest
- **For energetic vibe**: Sunset or Rose
- **For minimal design**: Slate
- **For creative work**: Violet

## 🐛 Troubleshooting

### Theme not changing?
→ Clear browser cache and refresh

### CSS not applied?
→ Check browser console for errors
→ Verify theme name is valid

### Theme not persisting?
→ Check session state: `st.session_state.current_theme`

## 🔗 Related Files

- Theme Manager: `utils/theme_manager.py`
- Base UI: `ui/base_ui.py`
- Main App: `main.py`
- Bootstrap CDN: v5.3.0

---

**Need more info?** See `THEMES.md` for comprehensive documentation
