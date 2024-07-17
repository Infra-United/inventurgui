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
- sets minimum widths to
    - 130 for the second (pinned) column, the Names of the Objects 
    - 250 for the third column (Description)
    - 40 for the fourth column (Number/Count)
    - 90 for the fith column (Package)

## Roadmap
### Make config available in admin page
- create /admin page with login
- create a nice input form for config values
- make use of those values

### Add Links with Information
- Add another column for Links ✅
- display them in a nice and small way (maybe emoji) ✅
- Add Links to the .ods-sheet

### Send a Request
- add option to select multiple things in grids ✅
- make selections visible in another tab
- add option to edit the number
- add option to send a mail with the list or something similar