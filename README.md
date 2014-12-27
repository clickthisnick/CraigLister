CraigLister
===========

This program will repeatedly post your craigslist ads every 72 hours and auto approve them.

It is useful when you want something to sell put you don't want to repeatedly post them.

It is built using selenium, it automates the browser actions and uses a gmail library to approve listings.

Dependencies
------------

This program uses the gmail library found here:

https://github.com/charlierguo/gmail/tree/master/gmail

Also you need chromedriver as found here:

http://chromedriver.storage.googleapis.com/index.html

Pillow

Python imaging library. To install use "pip install Pillow".
If you have an error you may need to "pip uninstall PIL" and reistall Pillow as well.

Usage
-----

| Steps | Action |
--------|--------|
| 1 | Make a new directory and put craigslister.py in it |
| 2 | Download the chromedriver and put into the craigslister directory |
| 3 | Install and import the gmail library or download files from gmail link and put in craiglister directory |
| 4 | Change the gmail username/pass in the craiglister.py file
| 5 | Run the craigslister.py file, it will create a readme, exampleinfo file, and a posts directory |
| 6 | In the posts folder create a new folder that describes the item to post |
| 7 | For example make a folder Guitar |
| 8 | Then copy exampleinfo.txt into the Guitar folder and rename info.txt |
| 9 | Fill out the info.txt with the correct craigslist information |
| 10 | Put any pictures you want in the listing in the Guitar folder |
| 11 | You can change the order of the images by naming appending _1 _2 _3 etc. |
| 12 | Run craigslister.py and it will post your Guitar listing |

This script works by parsing the info.txt file, filling out the craigslist post with that information, uploading the pictures and then submitting the post. Craigslist will then email you an approval link, the gmail library will parse that link and selenium will direct you to that link and click accept. Then the folder you created for that post will get moved to a posted folder within a date folder. Then when it has been 72 hours or greater the posts within that date folder will be moved back to the posts pool and will get posted again.

