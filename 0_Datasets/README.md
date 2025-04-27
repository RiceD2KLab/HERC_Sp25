# **Dataset Description README**

## **Overview**  
This repository contains datasets covering Texas school districts' **demographic** and **outcome oriented** data from **2018 to 2024**.  

- **Source:** [Texas Academic Performance Reports (TAPR)](https://rptsvr1.tea.texas.gov/perfreport/tapr/2023/download/DownloadData.html)  
- **Focus:** District-level data only.

---

## **Primary Folder: 1.0MergedData**  

- The `1.0MergedData` folder will serve as the **main source** for analysis moving forward.  
- Inside this folder are **individual merged files by year** (`merged_{year}`), each containing a **clean and combined** version of the following district-level datasets:
  - **GRAD:** Graduation, attendance, chronic absenteeism, dropout rates
  - **PERF1:** College, career, and military readiness (CCMR), TSIA, College Prep
  - **PERF2:** AP/IB exam results, SAT/ACT results
  - **PROF:** Staff and student profiles, graduate profiles
  - **STAAR1:** STAAR Assessment results (Grades 3–8)
  - **REF:** Geographical district information
  - **District Type**: TEA district classification (urban, rural, etc)
- **Years Covered:** 2020–2024  
- These files are fully integrated and ready for feature engineering and analysis.

---

## **Individual Non-Merged Yearly Data**  

The `Data{year}` folders contain **separate datasets** for each academic year, organized by **district**, **regional**, and **state** levels.  

- **Raw Files:**  
  - Direct downloads from the TEA website.  
  - **No cleaning or standardization** applied.  

- **Clean Files:**  
  - Datasets that have been **cleaned** and **standardized individually**.  
  - **No merging** — each dataset remains separate by reporting category.

- **Format Standards:**  
  - Consistent folder structure for **2020–2023**.  
  - **Exceptions:**  
    - **2018, 2019, and 2024** follow a different format due to changes in TEA data reporting.

---

## **Important Notes**  

- **Academic Year Naming:**  
  - The dataset year corresponds to the **second** year of the academic cycle (e.g., `2020` = 2019–2020 school year).

- **Data Cleaning Standards:**  
  - **2018–2019:** Older TEA format (custom cleaning).  
  - **2020–2023:** Standardized cleaning process.  
  - **2024:** New format adjustments (different from 2020–2023).

- **Geometry Folder:**  
  - Contains files used for **map visualizations** in R.
