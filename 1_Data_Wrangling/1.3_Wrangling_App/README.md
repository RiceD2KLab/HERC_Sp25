## TAPR Scraper GUI Downloadable Application README

```markdown
# TAPR Scraper GUI

This is a PyQt5 desktop application for scraping and processing Texas Academic Performance Report (TAPR) data. It uses Selenium to automate browser actions and BeautifulSoup for parsing downloaded content.

---

## 📦 Requirements

- Python 3.9–3.12
- Windows OS (for building)
- Nuitka (Python-to-exe compiler)

---

## 🧱 Setup Instructions

### 1. Clone or download the project files

Make sure your folder includes:
- `TAPR_Scraper.py` (GUI entry point)
- `scraping.py` (scraper logic)
- `wrangling.py` (data cleaning logic)
- `requirements.txt`

---

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Compile to `.exe` using Nuitka

Make sure Nuitka is installed:

```bash
pip install nuitka
```

Then run the following build command:

```bash
nuitka TAPR_Scraper.py ^
  --standalone ^
  --onefile ^
  --enable-plugin=pyqt5 ^
  --windows-disable-console ^
  --output-dir=dist_final
```

> ⚠️ Use `^` on Windows for line breaks. On macOS/Linux, use `\` or a single line.

---

### 5. Locate your final executable

The generated `.exe` will be in:

```
dist_final/TAPR_Scraper.exe
```

This file is fully portable and can be shared with others — no Python install needed.

---

## 🧪 Debugging Tips

- If nothing happens when you open the `.exe`, rebuild without `--windows-disable-console` to see errors.
- For faster testing, use a regular `--standalone` build without `--onefile`.

---
```

---

## ✅ 2. `requirements.txt` — How It Works + What to Use

### ✳️ Copy and paste this:
```txt
selenium
webdriver-manager
requests
beautifulsoup4
pandas
numpy
PyQt5
```

> You don’t need to list versions **unless** you're targeting a specific version for compatibility.

---

### 🧪 How to install from `requirements.txt`:

After activating your virtual environment, just run:

```bash
pip install -r requirements.txt
```

This command reads each line from `requirements.txt` and installs the corresponding packages via `pip`.

