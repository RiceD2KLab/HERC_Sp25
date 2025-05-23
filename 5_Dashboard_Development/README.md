# 5 - Dashboard Development

This directory contains files relating to developing a Shiny for Python dashboard. In the App folder, you will find all files necessary for the bundle that was used to create the DistrictMatch Shiny Application, which you can access here: https://kinderherc.shinyapps.io/districtmatch/. The data subdirectory houses all of the data files used by the dashboard. 

## App Subdirectories

1. **modules:** this houses the UI and server components of each navigation panel. 
2. **utils:** stores the functions necessary to generate plots and run the nearest neighbors model. See the directory README for more information on what is in each file.
3. **static:** stores images such as logos and the CSS stylesheet.
4. **data:** stores data frames while we work on integration with Box.

## How To Run The App

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RiceD2KLab/HERC_Sp25.git
2. **Navigate to the project directory:** 
   ```bash
   cd HERC_Sp25/5_Dashboard_Development
3. **Create a virtual environment:**
- **On Windows:**
  ```bash
  py -3.12 -m venv .venv
- **On macOS/Linux:**
  ```bash
  python3.12 -m venv .venv
4. **Activate the Virtual Environment**
- **On Windows:**
  ```bash
  .venv\Scripts\activate
- **On macOS/Linux:**
  ```bash
  source .venv/bin/activate
5. **Install the required libraries:**
   ```bash
   pip install -r requirements.txt

6. **Run the app in terminal using**
   ```bash
   shiny run app.py
   ```
