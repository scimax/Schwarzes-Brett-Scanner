# SchwarzesBrettScanner
This python module aims on scanning the housing advertisements on the [Schwarzes Brett Bremen](http://schwarzesbrett.bremen.de/verkauf-angebote/rubrik/wohnung-mietangebote-verkauf.html) periodicially to send notifications when a new ad is posted.

# Requirements
The module is written for [python3](https://www.python.org/). Besides python the modules listed in *requirements.txt* are used. 
All required modules can be installed via 
```sh
pip install -r requirements.txt
```
The SMS notification is based on [textbelt](https://textbelt.com/). In order to send SMS with the module, you need a valid key and remaining quota.

# Usage
Either place the module directory in your "lib/site-packages" of your python path to import it, or place the repository in the same directory as your main script. To use 


```python
from SchwarzesBrettScanner.scanner import SchwarzesBrettScanner
scanner = SchwarzesBrettScanner(30, "aaabbbbccccdddd", ["+490000000000"])
scanner.run()
```
where `aaabbbbccccdddd` is ypur key retrieved from textbelt and `["+490000000000"]` is the list of telephone numbers to which you want to send the SMS

