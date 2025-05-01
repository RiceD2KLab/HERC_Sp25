# TAPR Scraper GUI

This is a PyQt6 desktop application that scrapes and processes Texas Academic Performance Report (TAPR) data. It automates data collection using Selenium and displays a user-friendly GUI via PyQt.

---

## 📦 Requirements

- Python 3.9–3.12
- Windows OS (for packaging into `.exe`)
- Nuitka compiler
- All Python packages listed in `requirements.txt`

---

## ⚙️ Setup & Build Instructions

### 1. Clone or download this project

Make sure the following files are in your working directory:

- `TAPR_Scraper.py` (main GUI script)
- `scraping.py` (scraper logic)
- `wrangling.py` (data wrangling logic)
- `requirements.txt`

---

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 3. Install required Python packages
```bash
pip install -r requirements.txt
```

### 4. Install Nuitka (the Python-to-.exe compiler)
```bash
pip install nuitka
```

### 5. Build the final standalone .exe
```bash
nuitka TAPR_Scraper.py ^
  --standalone ^
  --onefile ^
  --enable-plugin=pyqt6 ^
  --windows-disable-console ^
  --output-dir=dist_final
```
This will create a single distributable .exe located at:
dist_final/TAPR_Scraper.exe


### 🧪 Notes
If the executable silently fails, rebuild without --windows-disable-console to reveal any errors in the terminal window.

For faster iteration during testing, use --standalone without --onefile.

You can safely share the final .exe with others — it does not require them to install Python.
