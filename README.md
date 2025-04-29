# DistrictMatch: Empowering Public Education with District Comparison


## Table of Contents 
1. [Overview](#overview)
2. [Installation](#installation)
3. [Dataset Description](#dataset-description)
4. [Data Wrangling](#data-wrangling)
5. [Data Exploration](#data-exploration)
6. [Feature_Engineering](#feature-engineering)
8. [Data Modeling](#data-modeling)
9. Dashboard Development
10. [Team Members & Contact Information](#team-members--contact-information)
11. [License](#license)
12. [Acknowledgments](#acknowledgments)


## Overview

#### Project Overview
Texas school districts face increasing pressure to meet accountability standards, yet many lack the resources to effectively analyze performance data. While public datasets exist, they are often fragmented, inconsistent, and difficult to navigate.

Our project, supported by the Houston Education Research Consortium (HERC), simplifies this process by enabling districts to identify peer districts—those with similar demographics—for performance comparison and strategic collaboration. By providing a streamlined, data-driven approach, we help districts extract meaningful insights to drive informed decision-making and improve academic outcomes.

#### Objectives

In this semester, our team plans to build on the work done in Fall 2024, expanding on some of their strengths while addressing the areas they were unable to accomplish. Specifically, our objectives include:

* **Develop a User-Friendly Data Extraction Tool:** Create a web scraping tool that enables users to retrieve datasets from the TEA website, with the ability to update annually as new information is added, solving the problem of data becoming outdated. Unlike traditional methods that rely on data compression techniques like PCA, this tool will allow users to access complete, raw datasets while enhancing their usability through automated cleaning and standardization.

* **Facilitate Comparative Analysis Among School Districts:** Assist school districts in identifying and comparing themselves with similar districts by allowing users to select and prioritize relevant demographic features, thereby enhancing data-driven decision-making. The matching process should focus on demographic factors for similarities, rather than test scores and graduation rates, to allow districts to use those outcomes as a comparison after the fact.

* **Develop an Interactive Dashboard for District Comparisons:** Create a web-based or GUI-driven dashboard that allows users to visualize, compare, and analyze school district data interactively, making insights more accessible and actionable. This dashboard should be simpler and more applicable for districts than the one made in the prior semester. 



## Installation
1. **Ensure Python 3.12.4 is installed:**
Make sure you have Python 3.12.4 installed on your system. If not, download it from [Python's official website](https://www.python.org/downloads/release/python-31011/)

2. **Clone the repository:**
   ```bash
   git clone https://github.com/RiceD2KLab/HERC_Sp25.git

3. **Navigate to the project directory:** 
   ```bash
   cd HERC_Sp25

4. **Create a virtual environment:**
- **On Windows:**
  ```bash
   py -3.12 -m venv .venv

- **On macOS/Linux:**
  ```bash
   python3.12 -m venv .venv

5. **Activate the Virtual Environment**
- **On Windows:**
  ```bash
  .venv\Scripts\activate

- **On macOS/Linux:**
  ```bash
   source .venv/bin/activate

6. **Install the required libraries:**
   ```bash
   pip install -r requirements.txt

7. **Verify the setup** 
  Run the following command to ensure the environment is correctly configured:
   ```bash
     python -V
     pip list
   ```

## Dataset Description
   Please see [0_Datasets/README.md](0_Datasets/README.md) for detailed dataset descriptions.

## Data Wrangling
   Please see [1_Data_Wrangling/README.md](1_Data_Wrangling/README.md) for details on data cleaning and preprocessing. It contains the code utilized to webscrape, clean raw datasets, and create a GUI Scraper tool. 
##  Data Exploration
   Please see [2_Data_Exploration/README.md](2_Data_Exploration/README.md) for details on exploratory data analysis.
##  Feature Engineering
   Please see [3_Feature_Engineering/README.md](3_Feature_Engineering/README.md) for details on feature engineering
## Data Modeling
   Please see [4_Data_Modeling/README.md](4_Data_Modeling/README.md) for details on modeling approaches, training, and validation.
## Dashboard Development
   Please see [5_Dashboard_Development/README.md](5_Dashboard_Development/README.md) for details on the dashboard development.
## Team Members & Contact Information
Bianca Schutz: mbs5@rice.edu \
Everett Adkins: ena4@rice.edu \
Manav Mathur: mm175@rice.edu \
Sachin Shurpalekar: sss20@rice.edu \
Trey McCray: wlm2@rice.edu

## License

This project is licensed under the Rice University D2K License.

## Acknowledgments

- Special thanks to the sponsor HERC, Instructor Dr. Xinjie Lan, and PhD mentor Konstantin Larin for their guidance throughout this project.
- Thanks to the Texas Education Agency for making educational data accessible.
