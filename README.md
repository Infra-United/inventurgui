# inventurgui
Just testing if you can create a simple gui for an excel sheet quickly
Here is the flagship instance of this program: inventur.infraunited.org

## Features
### Data Handling
- reads data from an ods file
- creates a pandas DataFrame

### NiceGUI
- creates a nice header in primary & secondary color with the following tabs:
    - one Tab for displaying a Markdown-Based Help-Page (see "Hilfe-Vorlage.md")
    - one Tab with an AGGrid displaying everything
    - one Tab with AGGrid for each unique value in the first Column (Categories)

### AGGrids
- creates AGGrids under each Tab with the Data in each category
- makes filtering available to the 2nd, 3rd and 5th column
- pins the second column to the left, sorts it ascending order and changes the text-color to secondary color
- creates one column with ℹ️ icons that can be clicked on to open links with further information in new tab

## Roadmap
### Make config available in admin page
- create /admin page accessible through /login ✅
- use Box for config dot notation
- create a nice input form for config values
- make use of those values

### Send a Request
- add option to select multiple things in grids ✅
- make selections visible in another tab
- add option to edit the number
- add option to send a mail with the list or something similar