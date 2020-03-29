"""
snek.tests.test_snek.py Module: Basic tests for Snek.
"""
#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
import os
from shutil import rmtree

import pytest

from snek.snek import Snek
from snek.config import SnekConfig
from snek.tests import MOCKS_FOLDER

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------
CONFIG_ARGUMENTS = {
    'build_path': f'{MOCKS_FOLDER}/build',
    'content_path': f'{MOCKS_FOLDER}/content',
    'data_in_build': False,
    'data_path': f'{MOCKS_FOLDER}/data',
    'templates_path': f'{MOCKS_FOLDER}/templates',
    'js_path': f'{MOCKS_FOLDER}/js',
    'assets_path': f'{MOCKS_FOLDER}/assets',
    'css_path': f'{MOCKS_FOLDER}/css',
    'scss_active': True,
    'scss_path': f'{MOCKS_FOLDER}/scss',
    'scss_output_style': 'compressed'
}

#-------------------------------------------------------------------------------
# Test suites
#-------------------------------------------------------------------------------
def test_construct():
    """
    Tests instanciating Snek with valid an invalid config objects.    
    """
    #
    # Valid config
    #
    config = SnekConfig(**CONFIG_ARGUMENTS)
    assert Snek(config)

    # Invalid config
    with pytest.raises(Exception):
        Snek({})

    with pytest.raises(Exception):
        Snek(12)

    with pytest.raises(Exception):
        Snek(CONFIG_ARGUMENTS) # Valid arguments, but not as a SnekConfig object

def test_build_with_scss():
    """
    Test building the website with files from the 'mocks' folder.
    
    Success conditions
    ------------------
    - Data is accessible programmatically and can be edited
    - Sitemap is accessible programmatically
    - Pages are built based on content, selected template, and can access shared data.
    - SCSS is processed
    - assets files are copied
    - JS files are copies
    - Build report is accessible
    - The "data_in_build" option works, making shared data available as JSON in the build folder.
    - Simple CSS copy works when "scss_active" option is False
    """
    # Cleanup
    rmtree(CONFIG_ARGUMENTS['build_path'])

    # Snek init
    config = SnekConfig(**CONFIG_ARGUMENTS)
    website = Snek(config)

    #
    # Test: Data is accessible programmatically and can be edited (see mocks/data)
    #
    assert website.data
    assert website.data['test1']
    assert website.data['test1']['test-key']
    assert website.data['test2']
    assert website.data['test2']['test-key']
    assert website.data['subfolder']
    assert website.data['subfolder']['test2']
    assert website.data['subfolder']['test2']['test-key']
    assert website.data['subfolder']['subsubfolder']
    assert website.data['subfolder']['subsubfolder']['test3']
    assert website.data['subfolder']['subsubfolder']['test3']['test-key']
    assert website.data['subfolder']['subsubfolder']['test4']
    assert website.data['subfolder']['subsubfolder']['test4']['test-key']
    assert website.data['subfolder']['subsubfolder']['test5']
    assert website.data['subfolder']['subsubfolder']['test5']['test-key']
    

    # Test alterations
    website.data['test2'] = {'test-key': 'Lorem Ipsum'}
    assert website.data['test2']['test-key'] == 'Lorem Ipsum'

    del website.data['test2']
    assert 'test2' not in website.data.keys()

    #
    # Test: Content is accessible programmatically (see mocks/content)
    #

    # Associative sitemap
    assert website.sitemap
    assert website.sitemap['test1']
    assert website.sitemap['test1']['title']
    assert website.sitemap['subfolder']
    assert website.sitemap['subfolder']['test2']
    assert website.sitemap['subfolder']['test2']['title']
    assert website.sitemap['subfolder']['subsubfolder']
    assert website.sitemap['subfolder']['subsubfolder']['test3']
    assert website.sitemap['subfolder']['subsubfolder']['test3']['title']
    assert website.sitemap['subfolder']['subsubfolder']['test4']
    assert website.sitemap['subfolder']['subsubfolder']['test4']['title']
    assert website.sitemap['subfolder']['subsubfolder']['test5']
    assert website.sitemap['subfolder']['subsubfolder']['test5']['title']

    # Flat sitemap
    assert website.sitemap_flat
    assert len(website.sitemap_flat) == 5

    #
    # Build
    #
    assert website.build()

    #
    # Test: Pages are built based on content and can access shared data.
    #
    # A few notes:
    # ------------
    # - The `index.html` template contains a reference to shared data, to test the shared data feature
    # - The `alternate.html` template is used by `test2.json.md` to test the templates selection feature
    #
    assert os.path.exists(f"{CONFIG_ARGUMENTS['build_path']}/test1.html")
    assert os.path.exists(f"{CONFIG_ARGUMENTS['build_path']}/subfolder/test2.html")
    assert os.path.exists(f"{CONFIG_ARGUMENTS['build_path']}/subfolder/subsubfolder/test3.html")
    assert os.path.exists(f"{CONFIG_ARGUMENTS['build_path']}/subfolder/subsubfolder/test4.html")

    # test2.html (and only this file) should be using "alternate.html" as a template.
    test1_html_content = open(f"{CONFIG_ARGUMENTS['build_path']}/test1.html", 'r').read()
    test2_html_content = open(f"{CONFIG_ARGUMENTS['build_path']}/subfolder/test2.html", 'r').read()
    assert test1_html_content.find('ALTERNATIVE TEMPLATE') == -1
    assert test2_html_content.find('ALTERNATIVE TEMPLATE')

    #
    # Test: SCSS is processed
    #
    assert os.path.exists(f"{CONFIG_ARGUMENTS['build_path']}/css/main.css")

    #
    # Test: assets files are copied
    #
    assert os.path.exists(f"{CONFIG_ARGUMENTS['build_path']}/assets/tux.svg")

    #
    # Test: JS files are copied
    #
    assert os.path.exists(f"{CONFIG_ARGUMENTS['build_path']}/js/main.js")

    #
    # Test: Build report is accessible
    #
    report = website.get_build_report()
    assert report
    assert report['build_start'] < report['build_end']

    #
    # Test: The "data in build" option works, making shared data available as JSON in the build folder.
    #

    # There is no "__data" folder in the current build
    assert not os.path.exists(f"{CONFIG_ARGUMENTS['build_path']}/__data")

    # Change config and rebuild
    website.config.data_in_build = True
    website.build()

    # "__data" should exist in new build, containing files from the shared data folder
    assert os.path.exists(f"{CONFIG_ARGUMENTS['build_path']}/__data")
    assert os.path.exists(f"{CONFIG_ARGUMENTS['build_path']}/__data/test1.json")
    assert os.path.exists(f"{CONFIG_ARGUMENTS['build_path']}/__data/subfolder/test2.json")

    #
    # Test: Simple CSS copy works when "scss_active" option is False
    #

    # scss_off_test.css should not exist in current build
    assert not os.path.exists(f"{CONFIG_ARGUMENTS['build_path']}/css/scss_off_test.css")

    # Change config and rebuild
    website.config.scss_active = False
    website.build()

    # scss_off_test.css should now exist in current build
    assert os.path.exists(f"{CONFIG_ARGUMENTS['build_path']}/css/scss_off_test.css")
