# **Building the TAPR Scraper Executable**  

This guide provides step-by-step instructions to **package the TAPR Scraper application into a standalone executable (.exe)** using `PyInstaller`.  

---

## **1. Setting Up the Environment**  

### **Step 1: Create and Activate a Virtual Environment**  
Open a terminal or command prompt and run:  
```sh
python -m venv venv
```
Activate the virtual environment:  

- **Windows:**  
  ```sh
  venv\Scripts\activate
  ```
- **Mac/Linux:**  
  ```sh
  source venv/bin/activate
  ```

### **Step 2: Install Dependencies**  
Install all necessary libraries:  
```sh
pip install -r requirements.txt
```

### **Step 3: Verify Installation**  
Confirm all dependencies are installed correctly:  
```sh
pip freeze
```

---

## **2. Testing and Building the Executable**  

### **Step 4: Test the Script Before Building**  
Before creating an `.exe`, run the script to ensure it works properly:  
```sh
python TAPR_Scraper.py
```

### **Step 5: Build the Executable**  
Use `PyInstaller` to generate a standalone `.exe` file:  
```sh
pyinstaller --onefile --noconsole --hidden-import=scraping --hidden-import=wrangling TAPR_Scraper.py
```

- `--onefile`: Packages everything into a single `.exe` file.  
- `--noconsole`: Prevents the console window from opening when the application runs.  
- `--hidden-import`: Ensures that all necessary modules are included.  

---

## **3. Managing Dependencies**  

### **Using a `requirements.txt` File** (Recommended)  
Instead of listing dependencies manually, create a `requirements.txt` file with:  
```sh
pip freeze > requirements.txt
```
Then, to install dependencies later:  
```sh
pip install -r requirements.txt
```

### **Dependencies List**  
For reference, these are the required dependencies:  
```txt
altgraph==0.17.4
attrs==25.1.0
beautifulsoup4==4.13.3
certifi==2025.1.31
cffi==1.17.1
charset-normalizer==3.4.1
et_xmlfile==2.0.0
h11==0.14.0
idna==3.10
numpy==2.2.3
openpyxl==3.1.5
outcome==1.3.0.post0
packaging==24.2
pandas==2.2.3
pefile==2023.2.7
pycparser==2.22
pyinstaller==6.12.0
pyinstaller-hooks-contrib==2025.1
PyQt6==6.8.1
PyQt6-Qt6==6.8.2
PyQt6_sip==13.10.0
PySocks==1.7.1
python-dateutil==2.9.0.post0
pytz==2025.1
pywin32-ctypes==0.2.3
requests==2.32.3
selenium==4.29.0
setuptools==75.8.0
six==1.17.0
sniffio==1.3.1
sortedcontainers==2.4.0
soupsieve==2.6
trio==0.29.0
trio-websocket==0.12.1
typing_extensions==4.12.2
tzdata==2025.1
urllib3==2.3.0
websocket-client==1.8.0
wsproto==1.2.0
```

---

## **4. Running the Application**  
Once the `.exe` is generated, it can be executed directly without requiring Python. Simply double-click the `.exe` file to launch the application.  

---

### **💡 Best Practices**  
- Always test your script **before** building the `.exe`.  
- Use a **virtual environment** to keep dependencies isolated.  
- **Store dependencies in `requirements.txt`** for easier installation and version control.  
- If using **third-party APIs**, check if additional authentication is needed after bundling.  

---

This version **follows industry standards**, making dependency management **easier and reproducible**. Let me know if you need further refinements! 🚀
