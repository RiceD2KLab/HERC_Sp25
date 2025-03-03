# Bridging the Data Gap: Empowering Texas School Districts with Analytics


## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Dataset Description](#dataset-description)
4. [Data Wrangling](#data-wrangling)
5. [Data Exploration](#data-exploration)
7. [Data Modeling](#data-modeling)
9. [Team Members & Contact Information](#team-members--contact-information)
10. [License](#license)
11. [Acknowledgments](#acknowledgments)


## Overview

#### Project Overview
Texas school districts face increasing pressure to meet accountability standards, yet many lack the resources to effectively analyze performance data. While public datasets exist, they are often fragmented, inconsistent, and difficult to navigate.

Our project, supported by the Houston Education Research Consortium (HERC), simplifies this process by enabling districts to identify peer districts—those with similar demographics—for performance comparison and strategic collaboration. By providing a streamlined, data-driven approach, we help districts extract meaningful insights to drive informed decision-making and improve academic outcomes.

#### Objectives

In this semester, our team plans to build on the work done in Fall 2024, expanding on some of their strengths while addressing the areas they were unable to accomplish. Specifically, our objectives include:

* **Develop a User-Friendly Data Extraction Tool:** Create a web scraping tool that enables users to retrieve datasets from the TEA website, with the ability to update annually as new information is added, solving the problem of data becoming outdated. Unlike traditional methods that rely on data compression techniques like PCA, this tool will allow users to access complete, raw datasets while enhancing their usability through automated cleaning and standardization.

* **Facilitate Comparative Analysis Among School Districts:** Assist school districts in identifying and comparing themselves with similar districts by allowing users to select and prioritize relevant demographic features, thereby enhancing data-driven decision-making. The matching process should focus on demographic factors for similarities, rather than test scores and graduation rates, to allow districts to use those outcomes as a comparison after the fact.

* **Engage and Collaborate with Local School Districts:** Actively consult with Houston area school districts to gather insights and feedback, ensuring the tool aligns with their specific needs and preferences, and provide comprehensive documentation to support its effective use. 

* **Develop an Interactive Dashboard for District Comparisons:** Create a web-based or GUI-driven dashboard that allows users to visualize, compare, and analyze school district data interactively, making insights more accessible and actionable. This dashboard should be simpler and more applicable for districts than the one made in the prior semester. 


#### Key Impacts

- **Efficient Decision-Making**: Instead of districts needing to deploy resources to sift through vast amounts of state educational data, the model and tooling provides a single source of truth, unifying all data sources into a single dataset and providing an immediate identification of a district's most similar peers.
- **Motivating Actionable Collaboration**: By highlighting comparable districts and the best areas they can learn from each other, the modeling encourages districts to tackle tailored areas for improvement and faciliate mutual knowledge transfer to best design policies tailored to their situations.
- **User-Friendly Access**: The visualization platform modernizes existening opaque and unintuive data access sources, simplifying access and analysis for district leaders across a range of technical and non-technical backgrounds.

This project is a practical and efficient solution to the challenge of understanding school district performance and improvement across Texas, enabling equitable access to a path towards stronger schools based on analyses extracted from data for every district in the state.


## Installation


## Running the Codebase
The codebase follows the data science pipeline and is mostly comprised of Jupyter notebooks. Thus, after performing the aforementioned installation to ensure the correct dependencies, please run the notebooks in the following directories in order (`01_Data_Wrangling`, `02_Data_Exploration`, `03_Feature_Engineering`, and `04_Data_Modeling`) to run the entire pipeline, or run specific subdirectories to perform one stage of the pipeline, as all intermediary data is saved and re-loaded in the next stage. The following five sections cover the subdirectories, starting with the datasets and then how the data is wrangled and explored, how feature engineering is conducted, and how the model is trained.

## Dataset Description
   Please see [00_Datasets/README.md](00_Datasets/README.md) for detailed dataset descriptions.

## Data Wrangling
   Please see [01_Data_Wrangling/README.md](01_Data_Wrangling/README.md) for details on data cleaning and preprocessing. It contains the code utilized to transform the raw data files into various cohesive datasets for exploration and modeling, as further detailed in the subdirectory.

##  Data Exploration
   Please see [02_Data_Exploration/README.md](02_Data_Exploration/README.md) for details on exploratory data analysis.

## Feature Engineering
   Please see [03_Feature_Engineering/README.md](03_Feature_Engineering/README.md) for details on feature processing to produce a refined feature space for modeling.

## Data Modeling
   Please see [04_Data_Modeling/README.md](04_Data_Modeling/README.md) for details on modeling approaches, training, and validation.


## Key Results and Verification
Although this project explored multiple modeling methods (all details for which can be found in [04_Data_Modeling/README.md](04_Data_Modeling/README.md)) the nonlinear autoencoder exhibited significantly better mean-squared error (MSE) than PCA or the linear autoencoder, and is adopted as the key model to generate scalar value representations for districts in calculating similarity. With these values normalized to [0,1], the following figure provides a visual representation of what potential key results are generated by this project's pipeline. This map allows for an easy visual identification of similarly performing districts, as districts with comparable characteristics share consistent colors, making patterns across Texas clearly discernible. 

Moreover, looking to both the condensed table to the left of the visualization, as well as the expanded table comparing both PCA values and nonlinear autoencoder bottle values, these results are in line with district rating, a pre-existing, manually-generated metric capturing district performance. Districts with higher performance as indicated by district rating correspond to lower autoencoder bottleneck values. Although the modeling does not indicate a district "ranking," the alignment of the autoencoder bottleneck values with a pre-existing standard for district evaluation helps to corroborate the validity of the results. Owing to the interconnected nature of features and the the inclusion of standardized test data comparing the autoencoder results to a pre-existing evaluation provides further confirmation that the calculated bottleneck values do capture meaningful characteristics of districts based on the data as well as the similarities and differences between them. Both PCA and the nonlinear autoencoder appear to capture these similarity patterns based on this manual verification method, again with the nonlinear autoencoder being utilized as the penultimate model due to better MSE.


<img src="./images/Final_Harris_Visualization.png" alt="Bottleneck Score Visualization Compared to District Rating in Harris County" width="800">
<img src="./images/Final_PCA_Autoencoder_Results.png" alt="Bottleneck Score Visualization Compared to District Rating in Harris County" width="800">

## Dashboard
The modeling results are presented intuitively to districts as an interactive visualization tool, incorporating key data points from the wrangled dataset, flexible geospatial visualizations, and multiple layers of data presentation methods to make the results accessible and equitable for all users of different technical backgrounds. The dashboard is powered by Tableau and is available at this [link](https://public.tableau.com/app/profile/wensheng.chu/viz/Texas_School_District_1125/DashboardSTAARAssessment) for dissemination to HERC, Harris county schools, and all districts in Texas.
![til](./assets/HERC_Dashboard_1125.gif)

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
