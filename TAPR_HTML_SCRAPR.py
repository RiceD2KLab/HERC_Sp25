import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import traceback
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# List of URLs to scrape
urls = [
    "https://rptsvr1.tea.texas.gov/perfreport/tapr/2023/xplore/ddrop_att.html",
    "https://rptsvr1.tea.texas.gov/perfreport/tapr/2023/download/diststaar1a.html",
    "https://rptsvr1.tea.texas.gov/perfreport/tapr/2023/download/diststaar1b.html",
    "https://rptsvr1.tea.texas.gov/perfreport/tapr/2023/download/dstaff.html",
    "https://rptsvr1.tea.texas.gov/perfreport/tapr/2023/download/dgrad1.html",
    "https://rptsvr1.tea.texas.gov/perfreport/tapr/2023/download/dstud.html",
    "https://rptsvr1.tea.texas.gov/perfreport/tapr/2023/download/dgrad.html"
]

# User-Agent header to mimic a real browser
headers_dict = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}

# List to store DataFrames
dataframes = []

# Iterate over URLs
for i, url in enumerate(urls):
    try:
        print(f"🔄 Scraping: {url}")

        # Send GET request with correct headers
        response = requests.get(url, headers=headers_dict, verify=False)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Locate the first table
        table = soup.find("table")

        if table:
            # Extract headers
            table_headers = [th.text.strip() for th in table.find_all("th")]

            # If no headers, create generic column names
            if not table_headers:
                table_headers = [f"Column_{j+1}" for j in range(len(table.find_all("tr")[1].find_all('td')))]

            # Extract table rows
            data = []
            for row in table.find_all("tr")[1:]:  # Skip header row
                cols = row.find_all("td")
                data.append([col.text.strip() for col in cols])

            # Convert to DataFrame
            df = pd.DataFrame(data, columns=table_headers)

            # Add a source column to identify where data came from
            df["Source_URL"] = url

            dataframes.append(df)
            print(f"✅ Successfully scraped {url} ({len(df)} rows)")

        else:
            print(f"⚠️ No table found on {url}")

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        traceback.print_exc()

    time.sleep(2)  # Avoid being blocked

# **Step 2: Combine and Save Data**
if dataframes:
    # Update file paths for VS Code environment
    ref_stu23 = pd.read_csv('/Users/treymccray/Downloads/ref_stu23.csv')  
    ref_staar23 = pd.read_csv('/Users/treymccray/Downloads/ref_staar23.csv')
    ref_attend_drop23 = pd.read_csv('/Users/treymccray/Downloads/ref_attend_drop23.csv')
    # Combine all scraped data into one DataFrame
    combined_df = pd.concat(dataframes, ignore_index=True).drop_duplicates()

    # Standardize names by replacing '21' or '22' with '23'
    combined_df['NAME_2'] = combined_df['NAME'].str.replace(r'21|22', '23', regex=True)

    # Merge with reference datasets
    ref_stu_new = ref_stu23.merge(combined_df, left_on='NAME', right_on='NAME_2', how='inner').drop_duplicates('NAME_x')
    ref_staar_new = ref_staar23.merge(combined_df, left_on='NAME', right_on='NAME_2', how='inner').drop_duplicates('NAME_x')
    ref_attend_drop_new = ref_attend_drop23.merge(combined_df, left_on='NAME', right_on='NAME_2', how='inner').drop_duplicates('NAME_x')

    # Display combined DataFrame (first 5 rows)
    print("\n📊 Combined DataFrame (First 5 Rows):")
    print(ref_stu_new.head())
    print(ref_staar_new.head())
    print(ref_attend_drop_new.head())

    # Save as CSV
    ref_stu_new.to_csv("ref_stu_new.csv", index=False)
    print(f"💾 Saved ref_stu_new.csv")
    ref_staar_new.to_csv("ref_staar_new.csv", index=False)
    print(f"💾 Saved ref_staar_new.csv")
    ref_attend_drop_new.to_csv("ref_attend_drop_new.csv", index=False)
    print(f"💾 Saved ref_attend_drop_new.csv")
else:
    print("⚠️ No data collected.")
