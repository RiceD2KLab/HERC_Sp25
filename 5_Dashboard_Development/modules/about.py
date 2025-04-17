### ABOUT PAGE ###
from shiny import ui, module

@module.ui
def about_ui():
    return ui.nav_panel(
        "About DistrictMatch", 
        ui.div(
                ui.img(src=str("Logo300x300.png"), height="300px"),  # Logo image
                style="text-align: center; margin-bottom: 20px;"  # Center-align the logo
            ),
        ui.TagList(
            ui.HTML("""
                <h3><strong>About DistrictMatch</strong></h3>
                <p>The DistrictMatch App is the creation of Team Kinder HERC from Rice University's Data to Knowledge Lab. The purpose of the app is to assist school districts in finding similar districts (neighbors) based upon their chosen demographic metrics. The tabs which will assist in district matching are “View My Matches”, “Why These Districts”, and “Understand Outcomes”. Furthermore, there is the 
                "How To Use" page which will directly explain how to navigate each of the DistrictMatch pages. </p>
                <h4><strong>View My Matches</strong></h4>
                <p>The "View My Matches" tab allows you to find districts similar to your selected district. You can view a specified number of matched districts. </p>                        
                <h4><strong>Why These Districts?</strong></h4>
                <p>The "Why These Districts" tab explains why your selected district was matched with specific neighboring districts. It provides visualizations that highlight similarities in key demographic features, allowing for more direct and meaningful comparisons across selected feature groups. </p>
                <h4><strong>Understand Outcomes</strong></h4> 
                <p>The "Understand Outcomes" tab serves as  way to view specific comparisons between your selected district and its neighboring districts based on certain outcomes data such as STAAR testing results, attendance, dropout rate and more.  </p>
            """)
        )
    )