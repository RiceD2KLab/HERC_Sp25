"""
Comprehensive Texas Academic Performance Report (TAPR) Data Scraper
This scraper allows users to select the level (Campus, District, Region, State) and type of data they would like to download from the TAPR data download on the TEA website. If the level is "D" for District, district type data will also be downloaded in addition to the TAPR data unless the user has indicated they do not want the data (set dist_type = False). 

If the files already exist, the scraper will not download new files. 

The scraper creates separate folders for each year of data and names the files with the appropriate year. 

"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
import os
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QComboBox, 
                            QPushButton, QTextEdit, QFileDialog)
from PyQt6.QtCore import QThread, pyqtSignal
import sys
from functools import partial
import ast



#District Type Scraper (Helper Function)
def district_type_scraper(year):
    """
    Scrapes the Texas Education Agency (TEA) website for district type data of a given school year.

    Args:
        year (int): The ending year of the school year (e.g., 2024 for the 2023-24 school year).

    Returns:
        pd.DataFrame: A DataFrame containing data from the specified school year's district type Excel file, 
                      or None if no file is found.

    Raises:
        requests.exceptions.RequestException: If there's an issue fetching the webpage.
    """
    school_year = f"{year-1}-{year-2000}"  # Convert to academic year format (e.g., "2023-24")
    url = f"https://tea.texas.gov/reports-and-data/school-data/district-type-data-search/district-type-{school_year}"

    try:
        # Attempt to get the webpage
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Warning: Could not access {url} (Status Code: {response.status_code})")
            return None  # Skip this year if the page is unavailable
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for Excel file links
        for link in soup.find_all("a", href=True):
            file_url = link.get('href')
            if file_url and re.search(r".xlsx$", file_url):
                full_url = f"https://tea.texas.gov{file_url}" if file_url.startswith("/") else file_url
                print(f"Found Excel file: {full_url}")
                return pd.read_excel(full_url, sheet_name=2)  # Read from the correct sheet
        
        print(f"Warning: No Excel file found on {url}")
        return None  # No file found, return None instead of breaking

    except requests.exceptions.RequestException as e:
        print(f"Error fetching district type data for {year}: {e}")
        return None
      
#Detects if files download within a given time limit, otherwise timesout (Helper Function)
def wait_for_downloads(variables, year, directory, timeout=200):
    """
    Waits for the expected data files to be downloaded within a specified timeout period.

    Args:
        variables (list of str): A list of variable names that determine expected file names.
        year (int): The year of the dataset, affecting file format (.dat for <2021, .csv for >=2021).
        directory (str): The directory where the files are expected to be downloaded.
        timeout (int, optional): Maximum time in seconds to wait for all files to be downloaded. Defaults to 200.

    Returns:
        bool: True if all expected files are downloaded within the timeout period, False otherwise.

    Raises:
        FileNotFoundError: If the specified directory does not exist.

    Notes:
        - The function checks for `.crdownload` files to ensure downloads are complete.
        - It waits in 5-second intervals before checking again.
        - If downloads complete within the timeout, a success message is printed.
    """
    start_time = time.time()  # Record the start time
    expected_files = []  # List to store expected file names based on year and variables

    # Determine expected file names based on the year
    for var in variables:
        if year < 2021:
            expected_files.append(f"DIST{var}.dat" if var != "REF" else "DREF.dat")
        else:
            expected_files.append(f"DIST{var}.csv" if var != "REF" else "DREF.csv")

    check = 1  # Variable to print waiting message only once
    while time.time() - start_time < timeout:  # Continue checking until timeout is reached
        downloaded_files = os.listdir(directory)  # Get the list of files in the directory

        # Check if all expected files are present and not still downloading (.crdownload files)
        if all(file in downloaded_files and not file.endswith(".crdownload") for file in expected_files):
            print(f"All downloads for {year} completed successfully.\n")
            return True  # Return True if all files are found and fully downloaded
        
        # Print waiting message only once at the start
        if check == 1:
            print("Waiting for all files to download...")
        check += 1

        time.sleep(5)  # Wait for 5 seconds before checking again

    return False  # Return False if the timeout is reached before all files are downloaded

#Renames files to include year in file name (Helper Function)
def file_renamer(directory, year, prefix, var, level):
    """
    Renames downloaded files in the specified directory based on naming conventions.

    Args:
        directory (str): The path to the directory containing the files.
        year (int): The year to be appended to the renamed files.
        prefix (str): The prefix used in some file names (e.g., 'DIST').
        var (str): The variable name (e.g., 'POP', 'ECON', 'REF').
        level (str): The level identifier (some files may use this instead of the prefix).

    Returns:
        None: The function renames files in place and does not return a value.

    Notes:
        - The function checks for `.csv` and `.dat` file extensions.
        - It looks for two possible naming patterns:
            1. `{prefix}{var}{ext}` (e.g., `DISTPOP.csv`)
            2. `{level}{var}{ext}` (e.g., `STATEPOP.dat`)
        - If a match is found, the file is renamed to:
            - `{level}{var}_{year}{ext}` for "REF" files.
            - `{prefix}{var}_{year}{ext}` for all other files.
        - The function **only renames the first matching file** and stops checking further.
    """
    for ext in ['.csv', '.dat']:  # Check both CSV and DAT file formats
        old_patterns = [
            f"{prefix}{var}{ext}",  # Pattern with prefix
            f"{level}{var}{ext}"     # Pattern with level (some files may not have prefix)
        ]

        for old_pattern in old_patterns:
            old_name = os.path.join(directory, old_pattern)  # Full path of the old file
            if os.path.exists(old_name):  # Check if file exists
                # Determine new name format
                if var == "REF":
                    new_name = os.path.join(directory, f"{level}{var}_{year}{ext}")
                else:
                    new_name = os.path.join(directory, f"{prefix}{var}_{year}{ext}")

                os.rename(old_name, new_name)  # Rename the file
                break  # Stop checking after renaming the first matching file



#Converts .dat files to .csv files automatically (Helper Function)
#Helper function: Converts .dat files to .csv files 
def convert_dat_to_csv(directory):
    """
    Converts all .dat files in the specified directory to .csv files.
    
    Parameters:
        directory (str): Path to the directory containing .dat files.
    """
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return

    # Iterate through files in the directory
    for file_name in os.listdir(directory):
        if file_name.endswith(".dat"):
            dat_file_path = os.path.join(directory, file_name)
            csv_file_path = os.path.join(directory, file_name.replace(".dat", ".csv"))

            try:
                # Read the .dat file with automatic delimiter detection
                df = pd.read_csv(dat_file_path, delimiter=None, engine='python')

                # Save as .csv
                df.to_csv(csv_file_path, index=False)
                print(f"Converted: {file_name} -> {csv_file_path}")

            except Exception as e:
                print(f"Error converting {file_name}: {e}")



#### Scrape Data from TAPR Advanced Download (Master Function)
def tea_scraper(directory_path, years, variables, level, dist_type=True):
    """
    Scrape all HERC data for specified years, variables, and level of data.
    
    Parameters:
        directory (string): file path that you would like data to be downloaded to
        years (list): List of years to scrape data for (formatted YYYY)
        variables (list): List of variable codes to download (such as "GRAD")
        level (str): Administrative level to scrape. Options:
            'C' for Campus
            'D' for District
            'R' for Region
            'S' for State

    Returns: 
        Specified files stored in folders located in users current directory. 
    """
    ### Checking to see if directory is a valid path and continuing code if it is  ### 
    if not os.path.isdir(directory_path):
        print(f"Error: {directory_path} is not a valid directory.")
        return
    print(f"Processing directory: {directory_path}")
    directory_path_name = directory_path

    ### Evaluating if level is accurate or not and converting it to expanded level name ### 
    valid_levels = {
        'C': 'Campus',
        'D': 'District',
        'R': 'Region',
        'S': 'State'
    }
    
    if level not in valid_levels:
        raise ValueError(f"Invalid level. Must be one of: {', '.join(valid_levels.keys())}")
    
    file_prefix = {
        'C': 'CAMP',
        'D': 'DIST',
        'R': 'REGN',
        'S': 'STATE'
    }[level]

    ### Looping through years to get data ### 
    for year in years:
        #Construct URL for TAPR data download page 
        url = f"https://rptsvr1.tea.texas.gov/perfreport/tapr/{year}/download/DownloadData.html"

        #Create a directory for current years data 
        dir_name = f"raw_data{year}"
        full_dir_path = os.path.join(directory_path_name, dir_name)
        os.makedirs(full_dir_path, exist_ok=True)
        
        #Set up chrome webdriver options 
        chrome_options = webdriver.ChromeOptions()
        absolute_download_path = os.path.abspath(full_dir_path)
        
        #Configure download prefrences to automate file saving 
        prefs = {
            "download.default_directory": absolute_download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_settings.popups": 0
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        try:
            #Initialive web scraper and navigate to the data download page 
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)

            # Check if the page loaded properly
            if "Page Not Found" in driver.page_source or "404" in driver.page_source:
                print(f"Year {year} does not exist. Skipping...")
                driver.quit()
                continue  # Skip this year and move to the next one
            #Select the desired level 
            level_select = driver.find_element(By.XPATH, f"//input[@type='radio' and @name='sumlev' and @value='{level}']")
            level_select.click()
        
        except WebDriverException as e:
            print(f"Failed to access {year}. Error: {e}")
            driver.quit()
            continue  # Skip this year

        unavailable = [] #Track unavilable files 
        print(f"Downloading {valid_levels[level]} Level TAPR Data for {year}...")
        
        # Loop through variables to download corresponding files 
        for var in variables:
            print(f"Checking for {file_prefix}{var} data...")
            #Define possible file patters to check if file is there 
            file_patterns = [
                f"{file_prefix}{var}_{year}.csv",
                f"{file_prefix}{var}_{year}.dat",
                f"{level}{var}_{year}.dat",
                f"{level}{var}_{year}.csv"
            ]
            
            # Skip downloading if the file already exists 
            if any(os.path.isfile(os.path.join(full_dir_path, file)) for file in file_patterns):
                print(f"{var}_{year} already exists")
                unavailable.append(var)
                continue
                
            try:
                #Select the dataset corresponding to the current variables 
                select_data = driver.find_element(By.XPATH, f"//input[@type='radio' and @name='setpick' and @value='{var}']")
                select_data.click()
                
                time.sleep(1)
                #Click continue button to initiate download 
                download = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Continue']")
                download.click()
                print(f"Downloaded {level if var == 'REF' else file_prefix}{var} for {year}")
                
            except NoSuchElementException:
                print(f"{var} not found for {year}")
                unavailable.append(var)
                continue
        
        #Get the list of successfully downloaded variables 
        available_vars = set(variables) - set(unavailable)

        #Wait for all downlods to complet and rename files accordingly 
        if wait_for_downloads(variables=available_vars, year=year, directory=full_dir_path):
            for a_var in available_vars:
                file_renamer(directory=full_dir_path, year=year, prefix=file_prefix, var=a_var, level=level)  
        driver.quit()

        #If downloading district level data, get the district type dataset 
        if level == "D" and dist_type:
            print(f"Downloading District Type Data for {year}...")
            
            if os.path.isfile(os.path.join(full_dir_path, f"district_type{year}.csv")):
                print(f"District Type Data for {year} already exists")
                print("")
                continue

            df = district_type_scraper(year)

            if df is None:
                print(f"Failed to retrieve District Type Data for {year}. Skipping...")
                continue  # Skip this year

            df.to_csv(os.path.join(full_dir_path, f"district_type{year}.csv"), index=False)
            print(f"Downloaded District Type Data for {year}")
            print("")

        #Calling helper function to convert .dat files to .csv files 
        convert_dat_to_csv(full_dir_path)

    print("All Data Downloaded!")



class ScraperWorker(QThread):
    """Worker thread to run the scraper without blocking the GUI"""
    progress = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, directory, years, variables, level):
        super().__init__()
        self.directory = directory
        self.years = years
        self.variables = variables
        self.level = level

    def run(self):
        # Redirect print statements to our progress signal
        import builtins
        original_print = builtins.print
        def custom_print(*args, **kwargs):
            # Convert args to string and emit as signal
            text = ' '.join(map(str, args))
            self.progress.emit(text)
            original_print(*args, **kwargs)
        
        builtins.print = custom_print
        
        try:
            tea_scraper(self.directory, self.years, self.variables, self.level)
        finally:
            builtins.print = original_print
            self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TEA Data Scraper")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Directory selection
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        dir_button = QPushButton("Browse...")
        dir_button.clicked.connect(self.browse_directory)
        dir_layout.addWidget(QLabel("Directory:"))
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(dir_button)
        layout.addLayout(dir_layout)

        # Years input
        years_layout = QHBoxLayout()
        self.years_input = QLineEdit()
        self.years_input.setPlaceholderText("e.g., [2020, 2021, 2022]")
        years_layout.addWidget(QLabel("Years:"))
        years_layout.addWidget(self.years_input)
        layout.addLayout(years_layout)

        # Variables input
        vars_layout = QHBoxLayout()
        self.vars_input = QLineEdit()
        self.vars_input.setPlaceholderText("e.g., ['GRAD', 'PROF', 'STAAR1']")
        vars_layout.addWidget(QLabel("Variables:"))
        vars_layout.addWidget(self.vars_input)
        layout.addLayout(vars_layout)

        # Level selection
        level_layout = QHBoxLayout()
        self.level_combo = QComboBox()
        self.level_combo.addItems(['Campus (C)', 'District (D)', 'Region (R)', 'State (S)'])
        level_layout.addWidget(QLabel("Level:"))
        level_layout.addWidget(self.level_combo)
        layout.addLayout(level_layout)

        # Progress display
        self.progress_display = QTextEdit()
        self.progress_display.setReadOnly(True)
        layout.addWidget(QLabel("Progress:"))
        layout.addWidget(self.progress_display)

        # Run button
        self.run_button = QPushButton("Run Scraper")
        self.run_button.clicked.connect(self.run_scraper)
        layout.addWidget(self.run_button)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.dir_input.setText(directory)

    def run_scraper(self):
        try:
            # Get and validate inputs
            directory = self.dir_input.text()
            years = ast.literal_eval(self.years_input.text())
            variables = ast.literal_eval(self.vars_input.text())
            level = self.level_combo.currentText()[0]  # Get first character (C, D, R, or S)

            # Disable run button
            self.run_button.setEnabled(False)
            
            # Clear previous progress
            self.progress_display.clear()

            # Create and start worker thread
            self.worker = ScraperWorker(directory, years, variables, level)
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.scraping_finished)
            self.worker.start()

        except Exception as e:
            self.progress_display.append(f"Error: {str(e)}")
            self.run_button.setEnabled(True)

    def update_progress(self, message):
        self.progress_display.append(message)
        # Scroll to bottom
        self.progress_display.verticalScrollBar().setValue(
            self.progress_display.verticalScrollBar().maximum()
        )

    def scraping_finished(self):
        self.run_button.setEnabled(True)
        self.progress_display.append("Scraping completed!")

# main.py (or add to gui_app.py)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())