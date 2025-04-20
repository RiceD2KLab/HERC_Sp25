### USER MANUAL ###

# =============================================================================
# 1. Imports
# =============================================================================
from shiny import ui, module


# =============================================================================
# 2. UI
# =============================================================================
@module.ui
def howto_ui():
    return ui.nav_panel(
        "How To Use DistrictMatch", 
        ui.TagList(
            ui.HTML("""    
                <h1 style="text-align:center; margin-bottom: 30px;">How To Use Each DistrictMatch Page</h1>
                    
                <figure style="text-align:center;">
                    <img src="ViewMyMatches.png" alt="View My Matches Overview" style="max-width:45%; height:auto;">
                    <figcaption style="margin-top: 10px; font-style: italic; color: #555;">View my matches page example</figcaption>
                </figure>

                <h3><strong>Using "View my matches" tab </strong></h3>
                <ul>
                    <li>On the left-hand side panel first choose a district under "Select District Name". This will act as the district you are finding similar districts to. </li>
                    <li>Select the feature groups under "Select Feature Group" to choose the demographic characteristics you consider important when identifying similar districts. </li>
                    <li>Choose how many similar districts you'd like to view by selecting a value under "Number of Neighbors". </li>
                    <li>Under "View Outcomes For," select the academic year you want to base the data on. For example, choosing 2024 will reflect data from the 2023–24 academic year. </li>
                    <li>Click the "Run Model" Button to populate neighbor districts. </li>
                    <li>Once the modeling is done you will be able to view a map of the resulting neighboring districts by district or county level. </li>
                    <li>The table on the far right will also display the districts that are most similar to your districts based on your selected parameters. </li>
                </ul>  
                <figure style="text-align:center;">
                    <img src="WhyTheseDistricts.png" alt="Why These Districts Overview" style="max-width:45%; height:auto;">
                    <figcaption style="margin-top: 10px; font-style: italic; color: #555;">Why these districts? page example</figcaption>
                </figure>    
                <h3><strong>Using "Why These Districts?" tab </strong></h3>
                <ul>
                    <li>This page displays visualizations that show how your selected district compares to its neighbors in terms of key demographic features. </li>
                    <li>The similarity of these plots depends on the feature groups you selected when running the matching model. </li>
                    <li>You can choose which specific demographic plots to view by toggling the checkboxes at the top of the page.</li>
                </ul>    
                <figure style="text-align:center;">
                    <img src="UnderstandOutcomes.png" alt="Understand Outcomes Overview" style="max-width:45%; height:auto;">
                    <figcaption style="margin-top: 10px; font-style: italic; color: #555;">Understand outcomes page example</figcaption>
                </figure>    
                <h3><strong>Using Understand outcomes</strong></h3>
                <ul>
                    <li>This page displays visualizations that show how your selected district compares to its neighbors in terms of key outcome features. </li>
                    <li>Using the "View An Outcome" dropdown, select which outcome variable you want to explore among neighbors. Make sure to toggle additional information if requested. </li>
                </ul>   
            """) #note to add pictures here
        )
    )