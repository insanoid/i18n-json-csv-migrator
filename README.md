# i18n-json-csv-migrator
CLI tool to quickly convert web-app localisation json file (i18n) into/back-into CSV for people who do not want to deal with JSON.

### Is this for you?
- Are you trying not to use external tools (POEditor, Transifex) in your toolchain to manage translations?
- Are people who manage content and translations (product/business-experts/marketing/design) non-technical and don't want to deal with JSON?
- Want to quickly translate your `.JSON` i18n language files into csv with each-language as columns for quick reference and translations.?
- Want to translate csv/spreadsheet with the key and the languages as columns into 1 JSON file per language (like `de-DE.json`, `en-gb.json`)
- Do you need a tool to quickly pull csv files from external sources into translation files in your JavaScript app?

**If any of the above your use-case? then this tool is for you.**

---
### How to use
- **To Extract (from JSON to CSV)**: `i18n_migrator merge --i18n-folder /path/to/folder/with/json --export-path /path/to/export/`
- **To Export (from CSV to JSON files)**: `i18n_migrator export --csv-file /path/to/csv-file --i18n-folder /path/to/folder/to/put/json`
- **To Test**: `poetry run pytest tests`

### How to develop
- Please use Pyenv to manage environment (built on python 3.7.6)
- Install Poetry: `pip install poetry`
- Install all packages: `poetry install`
- Run:
    - `poetry run black .`
    - `poetry run flake8`
    - `poetry run isort -y`.

### TODO/Improvements
- Ability to deal with variables not matching between language files
- Ability to retain sequence of keys/translations (from original source files)
- Integrate actions to test and create builds and releases.
- Build a UI to make it easy for users to use.
- Create a build to install directly instead of users having to build.
