Absolutely! Below are the two things you asked for:

---

## 📄 `README.md` — How to Build Executable Using Nuitka

```markdown
# TAPR Scraper GUI Application

This repository contains a PyQt-based GUI tool that automates the scraping and processing of Texas Academic Performance Reports (TAPR) data.

---

## ✅ Requirements

- Python 3.9–3.12
- Windows OS (for this build process)
- All dependencies listed in `requirements.txt`

---

## 🧱 Setup Instructions

### 1. Clone the repository or copy project files

Ensure these files are in your project folder:
- `TAPR_Scraper.py` (main GUI file)
- `scraping.py` (scraper functions)
- `wrangling.py` (data cleaning functions)

---

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

---

### 3. Install required packages

```bash
pip install -r requirements.txt
```

---

### 4. Build the executable with Nuitka

To build a fully standalone, one-file `.exe`:

```bash
nuitka TAPR_Scraper.py ^
  --standalone ^
  --onefile ^
  --enable-plugin=pyqt5 ^
  --windows-disable-console ^
  --output-dir=dist_final
```

> On macOS/Linux, replace `^` with `\` or just use a single line.

---

### 5. Find your output

After successful build, the final executable will be located in:

```
dist_final/TAPR_Scraper.exe
```

You can now share this file with others. No Python installation is required on their machine.

---

## 🧪 Tips

- If you want to test faster, skip `--onefile` to reduce build time.
- If errors occur, try removing `--windows-disable-console` to see error output.
```

---

## 📦 `requirements.txt` — Based on Your Imports

```txt
selenium
webdriver-manager
requests
beautifulsoup4
pandas
numpy
PyQt5
```

---

Let me know if you'd like:
- A Mac-specific version of the README
- A `build.bat` or `build.sh` file to automate the build process
