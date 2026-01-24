# 🚀 Quick Start - Bootstrap Multiple Themes

## ⚡ 30-Second Setup

### 1. Run the App
```bash
cd c:\Surajit\Python\OMR
streamlit run main.py
```

### 2. Find Theme Selector
Look in the top-right area for **"Select Theme:"** dropdown

### 3. Choose a Theme
```
Indigo  ← Professional (Default)
Ocean   ← Fresh & Calming
Forest  ← Natural & Organic
Sunset  ← Warm & Energetic
Violet  ← Bold & Creative
Slate   ← Classic & Minimal
Rose    ← Elegant & Premium
```

### 4. Enjoy!
The entire app updates instantly with your chosen theme! 🎨

---

## 📦 What's Available

### 7 Professional Themes
Each with carefully chosen colors, gradients, and styling

### Instant Switching
No page reload - just select and go!

### Session Persistence
Your theme choice is saved while you work

### Full Documentation
5 comprehensive guides included

---

## 🔍 Under the Hood

### What Was Added

```
✅ utils/theme_manager.py    (Theme system)
✅ Updated UI components     (Theme support)
✅ main.py                   (Theme selector)
✅ 5 Documentation files     (Complete guides)
```

### No Breaking Changes
Everything works as before, just with more options!

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `THEME_QUICK_REFERENCE.md` | Quick color & API reference |
| `THEMES.md` | Complete documentation |
| `THEME_IMPLEMENTATION.md` | Technical implementation |
| `THEME_SHOWCASE.md` | Visual showcase & recommendations |
| `THEME_SUMMARY.md` | Project summary |
| `COMPLETION_CHECKLIST.md` | Completion details |

---

## 💡 Tips

### Best Themes For Different Uses

**Professional Settings**
→ Indigo (default) or Slate

**Tech Companies**
→ Ocean or Violet

**Education/Non-Profit**
→ Forest

**Creative Industries**
→ Sunset or Violet

**Luxury/Premium Feel**
→ Rose

---

## 🛠️ For Developers

### Use a Specific Theme

```python
from ui import ExamPageUI

# Create page with ocean theme
exam = ExamPageUI(theme="ocean")
exam.render()
```

### Get Theme List

```python
from utils.theme_manager import ThemeManager

themes = ThemeManager.get_available_themes()
# ['indigo', 'ocean', 'forest', 'sunset', 'violet', 'slate', 'rose']
```

### Access Theme Colors

```python
theme = ThemeManager.get_theme("forest")

print(theme.primary)      # #059669
print(theme.accent)       # #34d399
print(theme.success)      # #059669
```

### Add Custom Theme

```python
from utils.theme_manager import ThemeManager, ThemeConfig

my_theme = ThemeConfig(
    primary="#your_color",
    primary_dark="#your_dark_color",
    # ... add all 15 colors
)

ThemeManager.THEMES["my_custom"] = my_theme
```

---

## ✨ Features

✅ **7 Professional Themes**
- Carefully designed color palettes
- WCAG AA accessibility compliant
- Professional appearance

✅ **Instant Switching**
- No page reload
- Smooth transitions
- Real-time updates

✅ **Easy to Customize**
- Add custom themes easily
- Extend color system
- Full control over styling

✅ **Complete Documentation**
- 5 comprehensive guides
- Code examples
- Troubleshooting tips

---

## 🎯 Common Tasks

### Change App Default Theme

In `main.py`, change:
```python
if "current_theme" not in st.session_state:
    st.session_state.current_theme = "indigo"  # Change this
```

### Remove Theme Selector

In `main.py`, comment out:
```python
# self.render_theme_selector()
```

### Add More Themes

In `utils/theme_manager.py`, add to `THEMES` dict:
```python
"my_theme": ThemeConfig(
    primary="#...",
    # ...
)
```

### Use Theme in Custom Component

```python
from utils.theme_manager import ThemeManager
import streamlit as st

theme = ThemeManager.get_theme(st.session_state.current_theme)
st.markdown(f"""
    <div style="color: {theme.primary};">
        My content
    </div>
""", unsafe_allow_html=True)
```

---

## 🐛 Troubleshooting

### Theme not appearing?
```python
# Check if theme exists
from utils.theme_manager import ThemeManager
print(ThemeManager.get_available_themes())
```

### Colors not changing?
- Clear browser cache (Ctrl+Shift+Delete)
- Refresh page (F5)
- Check session state: `st.session_state.current_theme`

### Custom theme not working?
- Verify all 14 colors are defined
- Check hex format (must start with #)
- Ensure theme is added to `ThemeManager.THEMES`

---

## 📊 Theme Comparison

```
┌─────────────────────────────────────────────┐
│ Theme    │ Mood          │ Best For         │
├─────────────────────────────────────────────┤
│ Indigo   │ Professional  │ Corporate        │
│ Ocean    │ Calm          │ Tech/SaaS        │
│ Forest   │ Natural       │ Education        │
│ Sunset   │ Energetic     │ Creative         │
│ Violet   │ Bold          │ Design           │
│ Slate    │ Minimal       │ Accessibility    │
│ Rose     │ Elegant       │ Luxury           │
└─────────────────────────────────────────────┘
```

---

## 🎓 Learn More

For detailed information, see:
- `THEME_QUICK_REFERENCE.md` - Quick reference
- `THEMES.md` - Complete guide
- `THEME_IMPLEMENTATION.md` - Technical details
- `THEME_SHOWCASE.md` - Visual showcase

---

## ✅ Ready to Go!

Your OMR application now has:
- ✨ 7 professional themes
- ✨ Instant theme switching
- ✨ Session persistence
- ✨ Complete documentation
- ✨ Easy customization

**Start using themes now!** 🎨

```bash
streamlit run main.py
```

---

**Questions?** Check the comprehensive documentation files!
