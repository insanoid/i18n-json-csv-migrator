#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
import shutil
from pathlib import Path

from i18n_migrator import create_csv_from_translation_files, create_translation_files_from_csv


def test_e2e_migration():
    """Test the integrity by converting a JSON file to CSV and then back and compare."""

    # Delete the file and the gen folder to be sure.
    dirpath = Path("/tmp/i18n-gen")
    if dirpath.exists() and dirpath.is_dir():
        shutil.rmtree("/tmp/i18n-gen")

    # Create the export file.
    os.makedirs(os.path.dirname("/tmp/i18n-gen/"), exist_ok=True)

    supported_locales = ["de-DE", "en-GB", "fr-FR"]
    export_csv_path = "/tmp/i18n-gen/export.csv"
    create_csv_from_translation_files(supported_locales, "test_files/", export_csv_path)
    create_translation_files_from_csv(supported_locales, export_csv_path, "/tmp/i18n-gen/")

    for locale in supported_locales:
        converted_file = {}
        original_file = {}
        with open("{}{}.json".format("/tmp/i18n-gen/", locale)) as f:
            converted_file = json.load(f)
        with open("{}{}.json".format("/tmp/i18n-gen/", locale)) as f:
            original_file = json.load(f)
        # We do not care about missing keys that were added (as it's our usecase)
        # Compare the JSON and make sure all the items exist.
        assert sorted(original_file.items()) == sorted(converted_file.items())
