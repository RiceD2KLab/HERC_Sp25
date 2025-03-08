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

## **1.3_Wrangling_App**
This folder contains the code for a **Python GUI application** that integrates web scraping and data cleaning into a user-friendly interface.

- **Components:**  
  - Combines **Web Scraping**, **Data Cleaning**, and **Python GUI** development.  
  - Streamlines the data acquisition and preprocessing workflow.  

For detailed instructions on how to install and use the GUI application, please refer to the **README file inside this folder**.

---
