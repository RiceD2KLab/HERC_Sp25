## TAPR Scraper Mac Version

This Mac Installer encapsulates the final TAPR Scraper version without the cleaning functionality. It allows Mac users to use the app to automatically scrape the raw data files of their choice from the TAPR Advanced Data Download page. Because the Windows version is packaged as a .exe, we created a .app version for Mac users since .exe files do not run on MacOS. This was bundled into a .app using Nuitka and downloads as a .dmg, allowing users to follow the steps below to move the app to their Applications folder and use the app as they would any other app on their Mac! 

## Instructions to Use Mac Scraping Application

### Download the .dmg
From the Google Drive, download the .dmg installer here: https://drive.google.com/file/d/1iyhG-yyNh_C61esBfIyqpgpHbXzJcvOY/view?usp=drive_link. You must specify that you would like to "Download anyways" as Google Drive will flag it as a potential virus. 

### Open the .dmg and bypass initial quarantine
1. Open the .dmg and drag the TEA Scraper App into your Applications folder. DO NOT OPEN THE APP!!
2. Open your terminal and run the command ```xattr -d com.apple.quarantine "/Applications/TEA Scraper.app"```.

### Open the Scraper App
1. You can now double-click the scraper app to open it.
2. You will likely receive a message saying "“TEA Scraper” Not Opened: Apple could not verify “TEA Scraper” is free of malware that may harm your Mac or compromise your privacy.". Click "Done".
3. Navigate to your System Settings > Privacy and Security. Scroll all the way down to "Security," where you should see a message saying, "TEA Scraper was blocked to protect your Mac."
4. Next to that message, click "Open Anyway".

### Use the Scraper!
The scraper should now work without any further need to deal with quarantine problems!
