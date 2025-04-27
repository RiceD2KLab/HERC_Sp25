# **Dataset Description README**  

## **Overview**  
This repository contains datasets covering Texas school districts' **demographics** and **outcome variables** from **2018 to 2024**.  

- **Data Source:** [Texas Academic Performance Reports (TAPR)](https://rptsvr1.tea.texas.gov/perfreport/tapr/2023/download/DownloadData.html)  
- **Focus:** Only **district-level** data is used in this analysis.  

---

## **Clean Data File Descriptions**

- **GRAD:** Attendance, Chronic Absenteeism, Graduation (RHSP/DAP & FHSP), and Dropout Rates  
- **PERF1:** Postsecondary Indicators: College, Career, and Military Readiness (CCMR), TSIA, College Prep
- **PERF2:** PERF2 Postsecondary Indicators: AP/IB, SAT/ACT
- **PROF:** Profile: Staff, Student, and Annual Graduates  
- **STAAR1:** STAAR Assessment Data (Primary Student Groups): Approaches, Meets, and Masters Grade Level (Grades 3 to 8)

---

### **Master Files Explained**  

The `0_Datasets/1.7Master_Files/Individual Year Files` folder contains the **result of merging** multiple datasets into a single dataset per year. These merged datasets combine critical performance and demographic indicators, simplifying the next stage of feature engineering. In order to combine all the files together you have to go to `HERC_Sp25/1_Data_Wrangling/1.2_Data_Cleaning/File_Merging` and use `Final_Mast_Sheet_ATT` to merge all of the individual year files together, make sure to download them to your desktop. 

### **Datasets Included in Merged Files:** GRAD, PERF1, PERF2, PROF, STAAR1
These **fully integrated datasets** will be used in the **next stage of feature engineering**, ensuring a more comprehensive analysis of district-level trends across Texas school districts.

---

## **Important Notes**  

### **Academic Year Naming**  
- Each **year refers to the second** year of the academic period.  
- Example: `2020` corresponds to the **2019-2020** school year.  

### **Data Cleaning Standards**  
- **2018 & 2019** data follows a **different methodology** due to structural changes in TEA data formatting. These years contain one single unified clean dataset that last semester's team worked on.  
- **2020-2023** datasets follow a **standardized** cleaning process.
- **2024** datasets follow a **different methodology** due to structural changes in TEA data formatting. 



### **Geometry Folder**  
- These files are datasets used to create map visualizations in R  



