# Feature Engineering
---
This folder contains the feature engineering notebooks used to prepare the data for the modeling phase of the analysis.  
The goal of this section is to select and organize the most helpful columns to be used for the upcoming data modeling work.  

We anticipate that most of the modeling will be built using the demographic features, while the outcome features will be used mainly for district comparison after the model is developed.
---
## Files Included

- **Demographic Feature Engineering.ipynb**  
  This notebook prepares the demographic data for modeling by:
  - Loading merged datasets.
  - Identifying and organizing relevant demographic columns into defined buckets.
  - Providing a standardized function to extract these columns from the desired year's dataset.

- **Outcome Feature Engineering.ipynb**  
  This notebook selects the outcome-oriented data columns and performs necessary transformations. Specifically, it:
  - Loads merged data from GitHub.
  - Performs transformations to STAAR test score data.
  - Calculates average dropout rates for grades 07–08 and 09–12 by student group.
  - Retrieves other relevant columns based on the specific year’s dataset.
