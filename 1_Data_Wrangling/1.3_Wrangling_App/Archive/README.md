# Welcome to the TAPR Scraper App! 🍵  

## Overview
The TAPR Scraper App allows users to efficiently download multiple files from the TAPR Advanced Download Website:
[Texas Academic Performance Reports (TAPR)
](https://rptsvr1.tea.texas.gov/perfreport/tapr/2023/download/DownloadData.html  )

This tool simplifies the process of retrieving datasets by enabling users to specify download parameters and execute a batch download.

## Features
* Download multiple raw TAPR datasets based on selected years and variables to a raw_data folder
* Choose the data level (e.g., campus, district, region, or state)
* Save files directly to a specified directory
* Automatically cleans all raw_data files into a new clean_data folder. (Properly formats NA values, maps column IDs with real column names, joins district/region IDs with true names)

## **Installation & Setup**  

The TAPR Scraper App is available for both **Windows** and **Mac** users. Follow the appropriate instructions below to install and run the application on your device.


### **Windows Installation**  
1. **Download the application:**  
   - Access the `.exe` file via Google Drive:  
     [TAPR Scraper for Windows](https://drive.google.com/drive/folders/1ee4Aw85x6BBq-QAIKfZ_aqhJ3FmCgcL6?usp=drive_link)  

2. **Run the installer:**  
   - Download `TAPR_Scraper.exe` to your preferred directory.  
   - Double-click the file to open the application.  
   - (Optional) Move the file to a permanent directory for easy access.  


### **Mac Installation**  

This Mac version allows users to scrape **raw data files** from the TAPR Advanced Data Download page. Due to macOS security restrictions, **the cleaning functionality is not included** in this version.  

#### **Step 1: Download the .dmg**  
- Download the **TAPR Scraper for Mac** from Google Drive:  
  [Download TAPR Scraper for Mac](https://drive.google.com/file/d/1iyhG-yyNh_C61esBfIyqpgpHbXzJcvOY/view?usp=drive_link)  
- When prompted, select **"Download Anyway"** (Google Drive may flag the file as a potential virus).  

#### **Step 2: Open the .dmg and Bypass Quarantine**  
1. Open the **.dmg** file and **drag the TEA Scraper App into your Applications folder**.  
   **⚠️ DO NOT open the app yet!**  
2. Open **Terminal** and run the following command to remove Apple’s quarantine flag:  
   ```sh
   xattr -d com.apple.quarantine "/Applications/TEA Scraper.app"
   ```

#### **Step 3: Open the Scraper App**  
1. Double-click the **TEA Scraper** app to open it.  
2. If you see the message:  
   > “TEA Scraper” Not Opened: Apple could not verify “TEA Scraper” is free of malware that may harm your Mac or compromise your privacy.  
   Click **"Done"** to close the window.  
3. Navigate to **System Settings > Privacy & Security**.  
4. Scroll down to the **Security** section. You should see a message stating:  
   > “TEA Scraper was blocked to protect your Mac.”  
5. Click **"Open Anyway"** next to this message.  

#### **Step 4: Use the Scraper!**  
- The scraper should now launch successfully without any further security issues.  

---

## How to Use the TAPR Scraping App
1. **Specify download directory:**  
   Select the directory where you want to save the downloaded data.  

2. **Enter Years:**  
   Provide the academic years you want to download, separated by commas, **inside square brackets** like this: `[2018, 2019, 2020]`.  
   Ensure that the years are **2018 and onwards**.  
   **Note:** The year corresponds to the latter half of an academic school year. For example, 2018 represents the 2017-2018 academic year.

4. **Enter data files you would like downloaded:**  
   Enter the variables (data files) that you wish to retrieve, **inside square brackets with each item in quotes**, like this: `["GRAD", "STAAR1", "PROF"]`.  

5. **Select Data Level:**  
   Choose the data level from the dropdown menu (Campus, District, Region, State).
   This parameter will affect the granularity of the data.   

6. **Run Scraper:**  
   Click **"Run Scraper"** to download the datasets. Files should be downloaded into the directory specified in step 1


## Variable Summary
Below are summaries of different data files available for download.  
Here's an overview of the various data files you can download  
* **STAAR1**: STAAR Assessment Data (Primary Student Groups): Approaches, Meets, and Masters Grade Level (Grades 3 to 8)
  
* **STAAR2**: STAAR Assessment Data (Primary Student Groups): Approaches, Meets, and Masters Grade Level (Grades 3 to 8)
  
* **STAAR3**: STAAR Assessment Data (Primary Student Groups): Academic Growth and Accelerated Learning
  
* **PART1**: STAAR Assessment Data (Primary Student Groups): Participation
  
* **STAAR4**: STAAR Assessment Data (Additional Student Groups): Approaches, Meets, and Masters Grade Level (Grades 3 to 8)
  
* **STAAR5**: STAAR Assessment Data (Additional Student Groups): Approaches, Meets, and Masters Grade Level (EOC, All Grades)
  
* **STAAR6**: STAAR Assessment Data (Additional Student Groups):  Academic Growth and Accelerated Learning

* **PART2**: STAAR Assessment Data (Additional Student Groups): Participation

* **STAAR_ADD1** Additional STAAR Assessment Data (TPRS Only): Rate by Enrolled Grade at Meets Grade Level or Above

* **GRAD**  Attendance, Chronic Absenteeism, Graduation (RHSP/DAP & FHSP), and Dropout Rates
  
* **COMP**  Attendance and Graduation  Longitudinal Rate (4-Year, 5-Year, & 6-Year)
  
* **PERF1** Postsecondary Indicators:  College, Career, and Military Readiness (CCMR), TSIA, College Prep

* **PERF2** Postsecondary Indicators:  AP/IB, SAT/ACT

* **PERF3** Postsecondary Indicators:  Advanced Courses, TX IHE

* **PROF**: Profile: Staff, Student, and Annual Graduates
  
* **KG**: Kindergarten Readiness (TPRS Only)
 
* **K_EFF**: Prekindergarten Effectiveness  


Primary Student Groups (2nd & 3rd position):
All Students (DA), African American (DB), Hispanic (DH), White (DW), American Indian (DI), Asian (D3), Pacific Islander (D4), Two or More Races (D2), Current Special Ed (DS), Former Special Ed (NS), Continuously Enrolled (NC), Non-Continuously Enrolled (NM), Economically Disadvantaged (DE), Current & Monitored EB/EL (D0), Current EB/EL (DL), At-Risk (DR), Male (DM), Female (DF)
 
Additional Student Groups (2nd & 3rd position):
Non-Special Ed (D6), Non-Econ Disadv (DN), Non-At-Risk (D7), Migrant (DG), Non-Migrant (D9), 1st Year Monitored EB/EL (DO), 2nd Year Monitored EB/EL (DP), Non-EB/EL (D8), LEP w/Services (D5)

  

