# **Building the TAPR Scraper Executable**  

This guide provides step-by-step instructions to **package the TAPR Scraper application into a standalone executable (.exe)** using `PyInstaller`.  

> ⚠️ **Note:** This process is designed for **Windows devices only**.  
> `.exe` files are Windows-native and will not run natively on Mac or Linux.

---

## **Quick Access**  
If you do not want to create the executable yourself, you can **directly download the pre-built `.exe` file** here:  
🔗 [TAPR Scraper Executable Download](https://rice.box.com/s/svclj7g4456unwqj006pilassonxrete)

Simply download the file and double-click to run — no Python installation required.

---

## **Why Create an Executable?**  
While `.py` scripts work perfectly for developers, they **require a full Python environment** to run.  
Creating a `.exe` allows you to:  
- **Distribute** the scraper to users who **do not have Python installed**.  
- **Simplify installation** — users can just double-click the `.exe` to launch the application.  
- **Make the scraper accessible** to a broader audience without needing a coding platform.

This step ensures that the TAPR Scraper can be **shared and used easily** outside of development environments.

---

## **1. Setting Up the Environment (Windows Only)**  

### **Step 1: Create and Activate a Virtual Environment**  
Open a terminal or command prompt and run:  
```bash
python -m venv venv
```
Activate the virtual environment:  
```bash
venv\Scripts\activate
```

### **Step 2: Install Dependencies**  
Install all necessary libraries using the provided `requirements.txt` file:  
```bash
pip install -r requirements.txt
```

### **Step 3: Verify Installation**  
Confirm all dependencies are installed correctly:  
```bash
pip freeze
```

---

## **2. Testing and Building the Executable**  

### **Step 4: Test the Script Before Building**  
Before creating an `.exe`, run the script to ensure it works properly:  
```bash
python TAPR_Scraper.py
```

### **Step 5: Build the Executable**  
Use `PyInstaller` to generate a standalone `.exe` file:  
```bash
pyinstaller --onefile --noconsole --hidden-import=scraping --hidden-import=wrangling TAPR_Scraper.py
```

- `--onefile`: Packages everything into a single `.exe` file.  
- `--noconsole`: Prevents the console window from opening when the application runs.  
- `--hidden-import`: Ensures that all necessary modules are included.

---

## **3. Running the Application**  
Once the `.exe` is generated, it can be executed directly without requiring Python.  
Simply double-click the `.exe` file to launch the application.

---

### **💡 Best Practices**  
- Always test your script **before** building the `.exe`.  
- Use a **virtual environment** to keep dependencies isolated.  
- **Store dependencies in `requirements.txt`** for easier installation and version control.  
- If using **third-party APIs**, check if additional authentication is needed after bundling.

