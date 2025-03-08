# **Dataset Description README**  

## **Overview**  
This repository contains **district-level** datasets covering Texas school districts' **demographics** and **performance metrics** from **2018 to 2023**.  

- **Data Source:** [Texas Academic Performance Reports (TAPR)](https://rptsvr1.tea.texas.gov/perfreport/tapr/2023/download/DownloadData.html)  
- **Focus:** Only **district-level** data is used in this analysis.  
- **For additional datasets, visit:** [INSERT Box Drive Link]  

---

## **Repository Structure**  

```
0_Datasets_csv/
    │   ├── Data2018/District/  → (2017-2018 school year)
    │   ├── Data2019/District/  → (2018-2019 school year)
    │   ├── Data2020/  → (2019-2020 school year)
    │   ├── Data2021/  → (2020-2021 school year)
    │   ├── Data2022/  → (2021-2022 school year)
    │   ├── Data2023/  → (2022-2023 school year)
    │   ├── Master_Files/  → (Combined yearly datasets)
    │   ├── Geometry/  → (Geographic Data Files)
    │   ├── Archive/  → (Old Unused Files)
```

### **Inside Each Year’s Folder (e.g., `Data2020/`)**
Each year contains three subfolders:
```
Data{Year}/
    ├── District/
    │   ├── raw_data/   → Unprocessed TEA files
    │   ├── clean_data/ → Pre-processed, structured datasets
    │
    ├── State/
    │   ├── raw_data/
    │   ├── clean_data/
    │
    ├── Region/
    │   ├── raw_data/
    │   ├── clean_data/
```

---

## **Important Notes**  

### **Academic Year Naming**  
- Each **year refers to the second** year of the academic period.  
- Example: `2020` corresponds to the **2019-2020** school year.  

### **Data Cleaning Standards**  
- **2020-2023** datasets follow a **standardized** cleaning process.  
- **2018 & 2019** data follows a **different methodology** due to structural changes in TEA data formatting. These years contain one single unified clean dataset that last semester's team worked on.  
- The **final combined district-level datasets** for 2018-2019 are stored separately.

### **Geometry Folder**  
- These files are datasets used to create map visualizations in R  

---

## **Clean Data File Descriptions**

- **GRAD:** Attendance, Chronic Absenteeism, Graduation (RHSP/DAP & FHSP), and Dropout Rates  
- **PERF1:** Postsecondary Indicators: College, Career, and Military Readiness (CCMR), TSIA, College Prep
- **PERF2:** PERF2 Postsecondary Indicators: AP/IB, SAT/ACT
- **PROF:** Profile: Staff, Student, and Annual Graduates  
- **STAAR1:** STAAR Assessment Data (Primary Student Groups): Approaches, Meets, and Masters Grade Level (Grades 3 to 8)  
