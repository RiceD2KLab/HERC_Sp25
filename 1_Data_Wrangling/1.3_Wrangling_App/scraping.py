"""
Comprehensive Texas Academic Performance Report (TAPR) Data Scraper
This scraper allows users to select the level (Campus, District, Region, State) and type of data they would like to download from the TAPR data download on the TEA website. If the level is "D" for District, district type data will also be downloaded in addition to the TAPR data unless the user has indicated they do not want the data (set dist_type = False).

If the files already exist, the scraper will not download new files.

The scraper creates separate folders for each year of data and names the files with the appropriate year.
"""

#Loading necessary packages
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
#from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException, NoSuchElementException
import os
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import random
import stat
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from io import BytesIO


### Helper Function 1: Scraping district type data
def district_type_scraper(year):
    """
    Scrapes the Texas Education Agency (TEA) website for district type data of a given school year.

    Args:
        year (int): The ending year of the school year (e.g., 2024 for the 2023-24 school year).

    Returns:
        pd.DataFrame: A DataFrame containing data from the specified school year's district type Excel file.

    Raises:
        requests.exceptions.RequestException: If there's an issue fetching the webpage.
        ValueError: If no Excel file is found on the page.   
    """
    print("District Type data is a district specific dataset!")
    school_year = f"{year-1}-{year%100}"
    url = f"https://tea.texas.gov/reports-and-data/school-data/district-type-data-search/district-type-{school_year}"

    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')

    for link in soup.find_all("a"):
        href = link.get('href')
        if href and re.search(r"\.xlsx$", href):
            file_url = f"https://tea.texas.gov{href}"
            file_response = requests.get(file_url, verify=False)
            return pd.read_excel(BytesIO(file_response.content), sheet_name=2)

    raise ValueError("No Excel file found on the page.")
      

### Helper Function 2: Ensure adequate time is given for files to properly download
def wait_for_downloads(variables, year, directory, level, timeout=200):
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
    file_prefix = {
        'C': 'CAMP',
        'D': 'DIST',
        'R': 'REGN',
        'S': 'STATE'
    }[level]

    start_time = time.time()  # Record the start time
    expected_files = []  # List to store expected file names based on year and variables

    # Determine expected file names based on the year
    for var in variables:
        if var == "REF":
            # Only add REF files if level is NOT 'S'
            if level != 'S':
                expected_files.append(f"{level}REF.dat" if year < 2021 else f"{level}REF.csv")
        else:
            expected_files.append(f"{file_prefix}{var}.dat" if year < 2021 else f"{file_prefix}{var}.csv")  

    check = 1  # Variable to print waiting message only once
    while time.time() - start_time < timeout:  # Continue checking until timeout is reached
        downloaded_files = os.listdir(directory)  # Get the list of files in the directory

        # Check if all expected files are present and not still downloading (.crdownload files)
        if all(file in downloaded_files and not file.endswith(".crdownload") for file in expected_files):
            print(f"All downloads for {year} completed successfully.\n")
            return True  # Return True if all files are found and fully downloaded
        
        # Print waiting message only once at the start
        if check == 1:
            print("Waiting for all files to download!...")
        check += 1

        time.sleep(5)  # Wait for 5 seconds before checking again

    return False  # Return False if the timeout is reached before all files are downloaded

### Helper Function 3: Rename file downloads to contain year in file name 
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


### Helper Function 4: Convert .dat files to .csv for better convenience
def convert_dat_to_csv(directory):
    """
    Converts all .dat files in the specified directory to .csv files and deletes the .dat files after conversion.
    
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

                # Delete the original .dat file after successful conversion
                os.remove(dat_file_path)
                print(f"Deleted original file: {file_name}")

            except Exception as e:
                print(f"Error converting {file_name}: {e}")

### Helper Function 5: Grab the column refrence files to join onto dataset in later steps 
def tea_reference_scraper(directory_path, year, level):
    """
    Scrape reference files for a specified year and level of data.
    
    Parameters:
        directory_path (str): File path where data should be downloaded.
        year (int): Year to scrape data for (formatted YYYY).
        level (str): Administrative level to scrape. Options:
            'C' -> 'campus', 'D' -> 'district', 'S' -> 'state', 'R' -> 'region'
    
    Returns: 
        Specified files stored in the given directory.
    """
    
    # Map shorthand inputs to full level names
    level_map = {'C': 'campus', 'D': 'district', 'S': 'state', 'R': 'region'}
    
    if level not in level_map:
        raise ValueError(f"Invalid level. Must be one of: {', '.join(level_map.keys())}")
    
    full_level_name = level_map[level]
    
    # Construct URL for TAPR data download page
    url = f"https://rptsvr1.tea.texas.gov/perfreport/tapr/{year}/download/DownloadData.html"
    
    # Ensure directory exists
    os.makedirs(directory_path, exist_ok=True)
    
    # Set up Chrome WebDriver options
    chrome_options = webdriver.ChromeOptions()
    absolute_download_path = os.path.abspath(directory_path)
    
    # Configure download preferences to automate file saving
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
        # Install and get path to chrome driver
        chromedriver_path = ChromeDriverManager().install()

        # Fix permissions on the chromedriver executable
        if os.name == 'posix':  # For Linux/Mac
            os.chmod(chromedriver_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
    
        # Create service with the driver path
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Add a delay before accessing the page
        time.sleep(random.uniform(3, 7))  # Wait between 3 to 7 seconds
        driver.get(url)
        
        # Check if the page loaded properly
        if "Page Not Found" in driver.page_source or "404" in driver.page_source:
            print(f"Year {year} does not exist. Skipping...")
            return
        
        print(f"Downloading reference file for {full_level_name} level, {year}...")
        file_name = f"TAPR_{full_level_name}_adv_{year}.xlsx"
        file_path = os.path.join(directory_path, file_name)
        
        # Skip downloading if the file already exists
        if os.path.isfile(file_path):
            print(f"{file_name} already exists")
            return
        
        try:
            # Find and click the link that corresponds to the required level
            link = driver.find_element(By.XPATH, f"//a[contains(text(), '{full_level_name}')]")
            link.click()
            print(f"Download initiated for {file_name}")
            
        except NoSuchElementException:
            print(f"Reference file link not found for {year}")
            return
        
        # Wait for the download to complete with an improved wait strategy
        download_timeout = 30  # Increased max wait time to 30 seconds
        elapsed_time = 0
        download_check_interval = 1  # Check every second
        
        while elapsed_time < download_timeout:
            if os.path.isfile(file_path):
                # Check if file download is complete (not a partial download)
                if not file_path.endswith('.crdownload') and not file_path.endswith('.tmp'):
                    print(f"Download completed for {file_name}")
                    break
            time.sleep(download_check_interval)
            elapsed_time += download_check_interval
            
            if elapsed_time % 5 == 0:
                print(f"Waiting for download... ({elapsed_time}s elapsed)")
        
        if not os.path.isfile(file_path) or file_path.endswith('.crdownload') or file_path.endswith('.tmp'):
            print(f"Download did not complete in time for {file_name}")
        
    except WebDriverException as e:
        print(f"Failed to access {year}. Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()
    
    print("Reference file download complete!!")


### Master Function: Combine helper functions to let you download specified ### 
### years, data files, and levels from TAPR advanced data download ### 
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
    #Appending REF files to the selected variables. This helps you encode the campus, district, and region ids
    variables.append('REF')

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
        if year <= 2023:
            url = f"https://rptsvr1.tea.texas.gov/perfreport/tapr/{year}/download/DownloadData.html"
        else: 
            url = f"https://rptsvr1.tea.texas.gov/perfreport/tapr/{year}/Advance%20Download/download-data-adv.html"

        #Create a directory for current years data 
        #dir_name = f"raw_data{year}"
        full_dir_path = os.path.join(directory_path_name, f"Data{year}", f"{valid_levels[level]}", f"raw_data")
        os.makedirs(full_dir_path, exist_ok=True)
                
        # Set up Chrome WebDriver options
        chrome_options = webdriver.ChromeOptions()
        absolute_download_path = os.path.abspath(full_dir_path)

        # Configure download preferences to automate file saving
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
            # Install and get path to chromedriver
            chromedriver_path = ChromeDriverManager().install()
            
            # Fix permissions on the chromedriver executable
            if os.name == 'posix':  # For Linux/Mac
                os.chmod(chromedriver_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
            
            # Create service with the driver path
            service = Service(chromedriver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            #Access the page
            driver.get(url)

            #Debugging for chrome driver path print statements: 
            print(f"ChromeDriver path: {chromedriver_path}")
            print(f"Operating system: {os.name}")

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

        ### REFRENCE FILE DATA DOWNLOAD: Calling helper function to download refrence file data
        tea_reference_scraper(full_dir_path, year, level)

        #Wait for all downlods to complet and rename files accordingly 
        if wait_for_downloads(variables=available_vars, year=year, directory=full_dir_path, level = level):
            for a_var in available_vars:
                file_renamer(directory=full_dir_path, year=year, prefix=file_prefix, var=a_var, level=level)  
        driver.quit()

        #Calling helper function to convert .dat files to .csv files 
        convert_dat_to_csv(full_dir_path)

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


    print("All Data Downloaded!")

    
