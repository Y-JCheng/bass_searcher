This is a bass searcher for bass buyers. To get it works, please run it on your local device.

Installing Instructions
-----------------------
1. Get your own YOUTUBE data API key (https://developers.google.com/youtube/registering_an_application)
    note. You don't need to apply for OAuth 2.0, only the API keys.
2. Create a file at the same folder as searcher.py called "APIkey.py", enter the following and save it.
    YOUTUBE_API_KEY = "YOUR_API_KEY_HERE"
2. Download everything to your computer.
3. Make sure you have every required python packages installed (see Required Python Packages below)
4. Run searcher.py with terminal.
5. Open your browser and type in http://127.0.0.1:5000/ in the address bar.
6. You are good to go!


Features - Bass Searcher
------------------------
1. You can do a quick search or add on any criteria in the advenced search.
2. You can click on the "Read more..." to see detailed information for the basses.
3. You can click on the "See video" to check the sound of the bass with a Youtube video.
4. If you want to buy it, click on the big orange button to go to the product page.


Features - Bass Brands
----------------------
1. You can check on all the brands in the Bass Brands page
2. "Learn more" buttons lead you to the official site of the brands. If the official site is not available, it lead you to Wikipedia page for the brand.
3. You can click on "See Analysis" button to see several charts about the bass industry


Required Python Packages
------------------------
1. request (https://requests.readthedocs.io/en/master/user/install/)
2. flask (https://flask.palletsprojects.com/en/1.1.x/installation/)
3. plotly (https://plotly.com/python/getting-started/)
4. bs4 (https://www.crummy.com/software/BeautifulSoup/bs4/doc/)