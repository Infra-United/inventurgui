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
- Translation: English and German already available - add your language with ease, by adding another .yml file to files/locales.
- Customization: any text and even all routes are customizable either through config or localization files

#### Optional: 📕 Wiki - Add your [Bookstack](https://www.bookstackapp.com/) Book as Wiki through the right drawer instead of a help page (Optional)

### Manage your Requests with ease
- Send automated E-Mails to you and your clients on each Request, Update or Deletion with an Overview, the editing link and an excel file containing the the requested items with all relevant data.
- You and your clients can use the magic editing link (no login required) to update and delete their requests.
- Your Clients see directly after requesting if their items are available in the requested timeframe or if there is an overlapping prior request. If there is an overlap, those items are marked red in the excel file.
- Stores requests with an overview of all requests per year, and the list for each request of course

#### Optional: Export all requests to excel and sync the file to your Nextcloud!

## Roadmap
### Make config available in admin page
- [x] create /admin page accessible through /login
- [ ] create a nice input form for config values

### Make everything even more customizable for different use cases
- [ ] Option to optimize for many small requests (e.g. overview per Month)
- [ ] Make Locations/Warehouses customizable so they can be managed by different groups
- [ ] Add optional map and calendar for use case in cities