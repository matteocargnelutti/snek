"""
snek.tests.test_snekconfig.py Module: Basic tests for SnekConfig.
"""
#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
import uuid

import pytest

from snek.snekconfig import SnekConfig
from snek.tests import MOCKS_FOLDER

#-------------------------------------------------------------------------------
# Test suites
#-------------------------------------------------------------------------------
def test_construct_invalid_arguments():
    """
    Tests instanciating SnekConfig with invalid arguments.
    """
    #
    # These arguments must raise an exception when passed to SnekConfig
    #
    invalid_arguments = [
        {'build_path': 12},
        {'content_path': 12},
        {'data_path': 12},
        {'templates_path': 12},
        {'js_path': 12},
        {'assets_path': 12},
        {'css_path': 12},
        {'scss_path': 12},
        {'content_path': f"./{uuid.uuid4()}"},
        {'data_path': f"./{uuid.uuid4()}"},
        {'templates_path': f"./{uuid.uuid4()}"},
        {'js_path': f"./{uuid.uuid4()}"},
        {'assets_path': f"./{uuid.uuid4()}"},
        {'css_path': f"./{uuid.uuid4()}"},
        {'scss_path': f"./{uuid.uuid4()}"}
    ]

    #
    # Test each invalid attribute
    #
    for arguments in invalid_arguments:
        with pytest.raises(Exception):

            # Special case: we need a valid build path to test all the parameters
            if arguments[0] != 'build_path':
                SnekConfig(build_path=f'{MOCKS_FOLDER}/build', **arguments)
            # If the current test is for invalid build_path
            else:
                SnekConfig(**arguments)

def test_construct_valid_arguments():
    """
    Tests instanciating SnekConfig with valid arguments.
    """
    config = SnekConfig(
        build_path=f'{MOCKS_FOLDER}/build',
        content_path=f'{MOCKS_FOLDER}/content',
        data_in_build=False,
        data_path=f'{MOCKS_FOLDER}/data',
        templates_path=f'{MOCKS_FOLDER}/templates',
        js_path=f'{MOCKS_FOLDER}/js',
        assets_path=f'{MOCKS_FOLDER}/assets',
        css_path=f'{MOCKS_FOLDER}/css',
        scss_active=True,
        scss_path=f'{MOCKS_FOLDER}/scss',
        scss_output_style='compressed'
    )
    assert config
