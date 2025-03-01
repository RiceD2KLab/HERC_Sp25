Pyinstaller Steps: 


Step 1: Create and Activate a Virtual Environment
python -m venv venv
venv\Scripts\activate


Step 2: Install All Dependencies
pip install pandas numpy selenium requests beautifulsoup4 pyqt6 pyinstaller openpyxl


Step 3: Verify All Dependencies
To confirm that everything is installed correctly:
pip freeze


Step 4: Test the Script Before Building
py TAPR_Scraper.py


Step 5: Use PyInstaller to Build the .exe File
pyinstaller --onefile --noconsole --hidden-import=scraping --hidden-import=wrangling TAPR_Scraper.py
c



Dependencies: 
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


