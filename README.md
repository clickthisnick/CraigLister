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
| 1 | Download the chromedriver and put into this directory |
| 2 | Install and import the gmail library or download files from gmail link and put in this directory |
| 3 | Change the gmail username/pass in the craiglister.py file
| 4 | In the listings folder create a new folder that describes the item to post and include pictures and a info.txt file |
| 5 | Look at the Example - Laptop folder for an idea of what the folder will be like, you can also add pictures in this folder |
| 6 | Run craigslister.py and it will post every listing in the listings folder |

This script works by parsing the info.txt file, filling out the craigslist post with that information, uploading the pictures and then submitting the post. Craigslist will then email you an approval link, the gmail library will parse that link and selenium will direct you to that link and click accept. Then the folder you created for that post will get moved to a posted folder within a date folder. Then when it has been 72 hours or greater the posts within that date folder will be moved back to the posts pool and will get posted again.
