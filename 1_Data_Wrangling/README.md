# **Data Wrangling README**  

This directory contains all scripts and tools related to extracting, cleaning, and processing data from the Texas Academic Performance Report (TAPR) online portal. It is organized into three main subfolders, each dedicated to a specific stage of data wrangling.

## **1.1_Web_Scraping**
This folder contains code for accessing the **TAPR online portal** and scraping files directly from the website.

- **Main Script:** `TEA_Scraper.ipynb`
- **Functionality:**  
  - Provides helper functions to automate data extraction.  
  - Allows users to specify the **level of data**, **years**, and **specific files** they want to download.  

## **1.2_Data_Cleaning**
This folder processes the **raw data** scraped in the previous step, ensuring consistency and usability.
- **Main Script:** `Data_Cleaning.ipynb`
- **Functionality:**  
  - Converts appropriate columns to numeric format.  
  - Replaces encoded missing values with standardized `NA`.  
  - Maps column IDs to human-readable column names.
  - Maps District/Region IDs to full names
- **Secondary Script:** `Yearly_Data_Merger.ipynb`
- **Functionality:**  
  - Reads in clean district datasets and merges it into one dataset by DISTRICT ID 


## **1.3_Wrangling_App**  
This folder contains the code for a **Python GUI application** that integrates web scraping and data cleaning into a user-friendly interface.

- **Components:**  
  - **scraping.py:**  
    - Functions originally developed in **1.1_Web_Scraping**, packaged into a `.py` script.  
  - **wrangling.py:**  
    - Functions originally developed in **1.2_Data_Cleaning**, packaged into a `.py` script.  
  - **TAPR_Scraper.py:**  
    - The **primary GUI application** that streamlines the **data acquisition** and **preprocessing** workflow.  
    - Integrates the scraping and cleaning functions into a single, interactive tool.  
  - **TAPR_Scraper_UserManual.pdf:**  
    - A user manual that provides detailed instructions on how to install, operate, and troubleshoot the TAPR scraping application.  

This app enables users to **easily scrape**, **clean**, and **prepare** Texas district data without needing to run Jupyter notebooks manually.


