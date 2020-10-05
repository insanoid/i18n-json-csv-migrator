#!/usr/bin/python

import csv
import glob
import json
import os

import click
import pandas as pd

BASE_KEY = "KEY"  # The column for the translation key in the csv.
EXPORT_FILE_NAME = "translation_export.csv"  # Default filename in which the file needs to be exported into.


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(version="0.1.0")
def i18n_migrator():
    """CLI tool to quickly convert web-app localisation json file (i18n) into/back-into CSV for people who do not want to deal with JSON."""
    pass


@i18n_migrator.command(
    "merge",
    short_help="Merge i18n JavaScript JSON files from the folder into 1 csv with language as columns.",
)
@click.option(
    "-f",
    "--i18n-folder",
    help="Folder to read files from",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    required=True,
)
@click.option(
    "-e",
    "--export-path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
    required=True,
)
def merge(**kwargs):
    """Merge i18n JavaScript JSON files from the folder into 1 csv with language as columns."""
    all_languages = [
        os.path.splitext(os.path.basename(path))[0] for path in glob.glob("{}/*.json".format(kwargs["i18n_folder"]))
    ]
    create_csv_from_translation_files(all_languages, kwargs["i18n_folder"], kwargs["export_path"])
    # TODO: Move this into the function where it finds languages from the folder.
    pass


@i18n_migrator.command(
    "export",
    short_help="Export the CSV file with languages as columns into individual language JSON i18n files.",
)
@click.option(
    "-f",
    "--i18n-folder",
    help="Folder to write files into",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
    required=True,
)
@click.option("-c", "--csv-file", type=click.File("rb"), required=True)
def export(**kwargs):
    """Merge i18n JavaScript JSON files from the folder into 1 csv with language as columns."""
    all_languages = [
        os.path.splitext(os.path.basename(path))[0] for path in glob.glob("{}/*.json".format(kwargs["i18n_folder"]))
    ]
    create_translation_files_from_csv(all_languages, kwargs["csv_file"], kwargs["i18n_folder"])


def create_csv_from_translation_files(supported_locales, base_url, export_path):
    """Export the translation files JSON into CSV with languages as columns"""
    csv_header_list = [BASE_KEY]  # The column for the translation key in the excel.
    csv_header_list.extend(supported_locales)  # Add each language as a column in the csv beforehand.

    # Add the header as the first row for the csv.
    all_translation_rows = [csv_header_list]

    # Store all translations per locale.
    translation_file_strings = {}

    for locale in supported_locales:
        # Reach each JSON file and pre-load the strings into dictionary.
        with open("{}/{}.json".format(base_url, locale)) as f:
            translation_file_strings[locale] = json.load(f)

    # Unmatched strings that don't exist in the first file
    # (we go through file #1 and keep remaining per language in this variable)./
    unmatched_strings = {}

    # Take the first file and use it as a base.
    first_locale_translation_strings = translation_file_strings[supported_locales[0]]
    for translation_key in first_locale_translation_strings:
        # Fill in the key in the first column.
        current_translation_row = [translation_key]

        for locale_idx, locale_code in enumerate(supported_locales):
            current_locale_strings = translation_file_strings[locale_code]
            if not not unmatched_strings.get(locale_code, None):
                current_locale_strings = unmatched_strings.get(
                    locale_code
                )  # Load unmatched string dictionary if it exists.

            translation = current_locale_strings.get(translation_key, None)
            # Remove the key from the locale dictionary, at the end only the unmatched strings will remain.
            if locale_idx != 0 and translation is not None:
                current_locale_strings.pop(translation_key)
            current_translation_row.append(translation)
            # Update the unmatched string with the current state.
            unmatched_strings[locale_code] = current_locale_strings
        all_translation_rows.append(current_translation_row)

    # Now we deal with the strings that were left-over (and did not exist in language file #1)
    # Since we already dealt with language file #1 we can remove the first file.
    unmatched_strings.pop(supported_locales[0])
    for locale_code, locale_translation_strings in unmatched_strings.items():

        for translation_key in locale_translation_strings.keys():
            # First item is the key, 2nd column is language file #1 - which we know does not have the key, hence will be blank.
            current_translation_row = [translation_key, ""]
            # See if the key exists in other locales maybe (maybe it just does not exist in the first locale)
            for current_locale_code in supported_locales[1:]:
                current_translation = unmatched_strings[current_locale_code].get(translation_key, "")
                if locale_code is not current_locale_code:
                    current_translation = unmatched_strings[current_locale_code].pop(translation_key, "")
                current_translation_row.append(current_translation)
            all_translation_rows.append(current_translation_row)

    # Count all the untranslated in the end
    # TODO: Could be optimised and done in the above loops.
    untranslated_count = {}
    for row in all_translation_rows:
        for idx, language_translation in enumerate(row[1:]):
            if not language_translation:
                current_langauge = supported_locales[idx]
                untranslated_count[current_langauge] = untranslated_count.get(current_langauge, 0) + 1

    untranslated_count_simplified = ["{} = {}".format(code, count) for code, count in untranslated_count.items()]
    print("Missing Translations: {}".format(", ".join(untranslated_count_simplified)))

    # We have a CSV, which we will now write to export path.
    # If it's a file then we write to file, if it's a path we export to the path with the default name.
    file_path = export_path
    if os.path.isdir(export_path) is True:
        file_path = "{}/{}".format(export_path, EXPORT_FILE_NAME)
    with open(file_path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(all_translation_rows)

    print("Wrote {} Strings: {}".format(len(all_translation_rows), file_path))


def create_translation_files_from_csv(supported_locales, file_url, export_path):
    """Export the translation CSV with languages as columns into JSON file per language"""
    df = pd.read_csv(file_url, na_values=[" ", ".", ""], keep_default_na=False, encoding="utf-8", engine="c")
    supported_locales = df.columns[1:]
    # Store all translations in a single object with key as the language code.
    translation_file_strings = {}
    print("Found {} Strings".format(len(df)))

    untranslated_count = {}
    for _, translation_row in df.iterrows():
        for locale_code in supported_locales:
            if translation_file_strings.get(locale_code) is None:
                translation_file_strings[locale_code] = {}
            # we don't include blank keys, as untranslated strings should not be considered in the file.
            if pd.isna(translation_row[locale_code]) is False:
                translation_file_strings[locale_code][translation_row[BASE_KEY]] = translation_row[locale_code]
            else:
                untranslated_count[locale_code] = untranslated_count.get(locale_code, 0) + 1

    print(untranslated_count)
    untranslated_count_simplified = ["{} = {}".format(code, count) for code, count in untranslated_count.items()]
    print("Missing Translations: {}".format(", ".join(untranslated_count_simplified)))

    for locale_code in supported_locales:
        with open("{}/{}.json".format(export_path, locale_code), "w+") as f:
            json.dump(translation_file_strings[locale_code], f, indent=2, ensure_ascii=False)
            print("Wrote File: {}{}.json".format(export_path, locale_code))


if __name__ == "__main__":
    i18n_migrator()
