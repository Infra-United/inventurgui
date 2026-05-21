# NiceShare (for Sharing Economies)
A Nice Software for sharing things - showcase your inventory, manage requests, include a Wiki, add thumbnails for your items.
</> on [Nicegui](https://nicegui.io/) with 💓. <br> Highly Customizable! -  Designed to make life for sharing economies easier - not harder - because most existing Software does not cover this use case.

Example Usage here: https://infra.uber.space

**Current Status**: *Almost Done - Ready for Production for Infra United - but not yet for simple usage in other environments.*

## Features
### Manage your Inventory and showcase your items
- Import Data from Excel (.xlsx) or Libre Office Calc (.ods)
- Define your own Schema (Columns) - See [Schema](#Schema)
- Group your inventory in Categories
- Add multiple Locations
- Login to the Admin Panel and add thumbnails to your items! 🖼️
- Uses [Polars](https://pola.rs) in Memory and [DuckDB](https://duckdb.org/) on Disk.

#### Optional: ⛅ Cloud Sync - Load all your custom data and pages from your [Nextcloud](https://nextcloud.com/) (through WebDav) - so everyone on your team can edit your website with ease! 

### Generate a highly customizable, intuitive and responsive Website
- Easily add custom Markdown Pages (Start, Terms, About, Help, etc.)
- Showcase your Inventory grouped by Location and Category through the left sidebar
- Streamlined Process for requesting items - simply follow the Floating Actions
- Generate a Request [Form](#Form) tailored to your needs - including input validation 
- Translate: English and German already available - add your language with ease, by adding another .yml file to files/locales.
- Customize: any text, icon, colors and even all routes are customizable either through config or localization files

#### Optional: Export all requests to excel and sync the file to your Nextcloud!

## Install
1) Clone this repository
2) cd into it
3) install uv if not already done: https://docs.astral.sh/uv/#installation
4) Run `uv run niceshare`
5) Copy files/default_config.yml to config.yml and edit it to your needs
6) Create a systemd service and set environment variables with your credentials 

## Configuration
### Config.yml
#### General settings

```yml
title: Website-Title
favicon: favicon.png
logo: logo.png
organization: My_Org (Used for filenames of Excel-Downloads)
domain: 'http://localhost:8080' (Full domain - used to set correct image links)
port: 8080
language: 'de' # The language to use on Quasar UI Components 
locale: 'de_DE.UTF-8' # Locale used for correct names of days, months, etc.
date_format: '%d.%m.%y' # The format for dates - see https://strftime.org/
time_format: '%H:%M' # The format for times - see https://strftime.org/
theme:
  primary: '#e89769'
  secondary: '#37474f'
  accent: '#607d8b'
  dark_page: '#0d1626'
  links: '#8ba3af'
  dark_mode: True
dav:
  dir: "My Folder/My Subfolder" (Path inside cloud to use for syncing)
  pull: # Map of filenames to pull - the keys are relevant!
    logo: 'logo.png'
    help: 'help.md'
    terms: 'terms.md'
    start: 'start.md'
    inventory: "IU_Inventur.xlsx"
mail:
  mail_to: 'requests@example.org' (Used for requests)
  admin: 'tech-admin@example.org' (Used for error Emails)
data:
  filename: "Inventory" (The filename of your inventory without file extension)
  warehouses: (The sheets in your inventory - hence the names of your warehouses)
    - "Mitte"
    - "Leipzig"
    - "Rheinland"
  columns: # The columns in your inventory tables)
    shelf: Regal # Not necessary
    category: Kategorie # Necessary!
    object: Objekt # Necessary!
    count: Zahl # Necessary!
    total: von # Necessary! (Is added automatically, does not have to be in inventory)
    pack: Packung # Not strictly necessary but useful for weight
    weight: kg # Necessary! (can be empty in inventory)
    total_weight: Gesamtgewicht # Necessary! (Is added automatically, does not have to be in inventory)
    comment: Kommentar # Not necessary (can also be empty in inventory)
    url: Link # Not necessary (can also be empty in inventory)
    image: Bild # Not necessary! (can also be empty in inventory)
```

#### Specific Page settings
The following blocks in config.yml all have a label and icon, some have a display and a path key.
- The "label" always determines the menu title, page title, route name, etc.
- The "icon" always has to be in https://fonts.google.com/icons?icon.set=Material%20Icons
- Using "path" you can specify a markdown file that will be rendered on that page
- Using "display" you can hide the page entirely (only available if page is not strictly necessary)

```yml
start:
  label: 'Start'
  icon: 'home'
  path: 'start.md'
help:
  display: true
  wiki: True (Set to false if you do not have a bookstack wiki)
  label: 'Wiki' 
  icon: 'menu_book'
  url: 'https://wiki.example.org/books/cmy-bookstack-book/export/html'
  path: 'my-bookstack-book.html' (Local Path of either a help.md or the html export of your wiki)
warehouse:
  label: 'Lager'
  icon: 'warehouse'
  everything: 'Alles'
  selection: 'Meine Auswahl'
cart:
  label: 'Palettieren'
  icon: 'sym_o_pallet'
  tab_icon: 'local_shipping'
form:
  label: 'Beladen' # The url path of the requests page
  icon: 'sym_o_forklift' # The menu icon for the requests page
  tab_label: 'Formular' # The label for the form tab on the page
  tab_icon: 'article' # The icon for the form tab on the page
  input: # Will create input fields at the start of the form for any number of items
    name: 'Camp/Organisation' # This key is required
    place: 'Ort'
    donation: 'Geplante Spende'
    email: 'E-Mail-Adresse'
    contact: 'Signal-Kontakt'
  message: 'Deine Nachricht'
  checkbox: # Will create checkboxes at the end of the form for any number of items
    terms: 'Ich habe die Leihbedingungen gelesen. *'
    mails: 'Ich bin einverstanden ein bis zwei Mal im Jahr den IU Newsletter zu bekommen. *'
  terms: # Show terms to the user in a tab next to the form
    display: true # Set this to false if you don't need this
    label: 'Leihbedingungen'
    icon: 'policy'
    path: 'terms.md'
finish:
  label: 'Abfahrt'
requests: # Only visible for admins and editors
  label: 'Anfragen'
  icon: 'drafts'
  filename: 'IU_Anfragen'
settings: # Only visible for admins and editors
  label: 'Einstellungen'
```

### Environment Variables
```dotenv
NEXTCLOUD_TOKEN=my-super-secret-nextcloud-app-token;
NEXTCLOUD_USER=exampleuser;
NEXTCLOUD_DOMAIN=cloud.example.org;
```

#### UI
```dotenv
UI_STORAGE_SECRET=somerandomstringlongenoughtobesafe;
UI_ADMIN_PASSWORD=some password you will use to log in to admin panel;
UI_AUTH_SECRET=somerandomstringlongerthan32characters;
```

#### Mail
``` dotenv
MAIL_USER=user@example.org;
MAIL_PORT=465;
MAIL_PASSWORD=my super secret mail password;
MAIL_DOMAIN=mailserver.example.org;
```


## Roadmap
### Make config available in admin page
- [x] create /admin page accessible through /login
- [ ] create a nice input form for config values

### Make everything even more customizable for different use cases
- [ ] Option to optimize for many small requests (e.g. overview per Month)
- [ ] Make Locations/Warehouses customizable so they can be managed by different groups
- [ ] Add optional map and calendar for use case in cities