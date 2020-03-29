"""
snek.tests.test_snekutils.py Module: Basic tests for SnekUtils.
"""
# -------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------
import os
import pytest
from pathlib import Path

import snek.utils
from snek.utils import SnekUtils as utils
from snek.utils import SnekDict
from snek.tests import MOCKS_FOLDER


def test_find_files():
    files = utils.find_files(where=MOCKS_FOLDER, suffixes=[".json", ".yaml", ".yml"])

    test1_json = Path(os.path.join(MOCKS_FOLDER, "data/test1.json")).resolve()
    assert test1_json in files

    files_md = utils.find_files(
        where=MOCKS_FOLDER, suffixes=[".json", ".yaml", ".yml"], extra_suffix=".md"
    )
    test1_json_md = Path(os.path.join(MOCKS_FOLDER, "content/test1.json.md")).resolve()
    assert test1_json_md in files_md


def test_get_nested_keys():
    test1_json = Path(os.path.join(MOCKS_FOLDER, "data/test1.json")).resolve()
    base_path = Path(MOCKS_FOLDER).resolve()

    keys = utils.get_nested_keys_from_filepath(
        test1_json, where=base_path, strip_suffixes=[".json"]
    )
    assert keys == ["data", "test1"]

def test_SnekDict():
    keys = ['level1', 'level2', 'level3', 'filename']
    attr = SnekDict()
    value = 'TEST'
    attr.update_from_nested_keys(keys, value)

    assert attr['level1']['level2']['level3']['filename'] == 'TEST'
    keys = ['level1', 'level2', 'level3', 'filename']
    value = 'TEST2'
    with pytest.raises(snek.utils.DuplicateKeyError):
        attr.update_from_nested_keys(keys, value)


    
