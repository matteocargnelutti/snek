"""
snek.snekconfig.py Module: Snek configuration object class
"""
#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
import os
import re

#-------------------------------------------------------------------------------
# SnekConfig class
#-------------------------------------------------------------------------------
class SnekConfig:
    """
    Snek's configuration class.
    Will use default values unless told otherwise.

    Attributes
    ----------
    build_path: str
        Path to the project's build destination. Will be created if it does not exists.
    content_path: str
        Path to the project's content files. Must exist.
    data_in_build: bool
        If True, will copy data files to the built websites so they can be accessed via JavScript.
    data_path: str
        Path to the project's data files.
    templates_path: str
        Path to the project's templates files.
    js_path: str
        Path to the project's JavaScript files.
    assets_path: str
        Path to the project's assets files.
    css_path: str
        Path to the project's CSS files. Ignored if scss_active is True.
    scss_active: bool
        Determines if files from the SASS folder should be processed instead of CSS.
    scss_path: str
        Path to the project's SASS files.
    scss_output_style: str
        Can be 'compressed' , 'nested' or 'expanded'.
    is_valid: bool
        Indicates if the current configuration is valid.
    """

    def __init__(self,
                 build_path='./build',
                 content_path='./content',
                 data_in_build=False,
                 data_path='./data',
                 templates_path='./templates',
                 js_path='./js',
                 assets_path='./assets',
                 css_path='./css',
                 scss_active=True,
                 scss_path='./scss',
                 scss_output_style='compressed'):
        """
        Constructor.

        Parameters
        ----------
        build_path: str (optional)
            See self.build_path. (defaults to './build')
        content_path: str (optional)
            See self.content_path. (defaults to './content')
        templates_path: str (optional)
            See self.templates_path (defaults to './templates')
        data_in_build: bool (optional)
            See self.data_in_build. (defaults to False)
        data_path: str (optional)
            See self.data_path. (defaults to './data')
        js_path: str (optional)
            See self.js_path. (defaults to './js')
        assets_path: str (optional)
            See self.assets_path. (defaults to './assets')
        css_path: str (optional)
            See self.css_path. Ignored if scss_active is True. (optional, defaults to './css')
        scss_active: bool (optional)
            See self.scss_active. (defaults to True)
        scss_path: str (optional)
            See self.scss_path. (defaults to './scss')
        scss_output_style: str (optional)
            See self.scss_output_style. (defaults to 'compressed')

        Returns
        -------
        SnekConfig
        """
        # For now, the configuration is considered valid
        self.is_valid = False

        #
        # Check the build folder: Loose attempt at creating it + check if exists.
        # If valid, keep in self.build_path
        #
        try:
            os.mkdir(build_path)
        except OSError: pass

        if not os.path.isdir(build_path):
            raise BuildFolderNotFound(f'Build folder not found. "{build_path}" provided.')

        self.build_path = build_path

        #
        # For all the other provided paths: make sure they are valid in format
        #
        paths_to_check = {
            'content_path': content_path,
            'data_path': data_path,
            'templates_path': templates_path,
            'js_path': js_path,
            'assets_path': assets_path,
            'scss_path': scss_path,
            'css_path': css_path
        }

        # Check that folders exist and keep as attributes
        for what, where in paths_to_check.items():

            if not re.match('(\\\\?([^\\/]*[\\/])*)([^\\/]+)$', where):
                raise InvalidPath(f"Invalid path provided for the {what} folder. '{where}' given.")

            where = os.path.normpath(where)
            self.__setattr__(f'{what}', where)

        #
        # Other parameters
        #
        self.scss_active = True if scss_active == True else False
        self.scss_output_style = scss_output_style if scss_output_style in ['compressed', 'nested', 'expanded'] else 'compressed'
        self.data_in_build = True if data_in_build == True else False

        #
        # If we reach this point, the configuration is valid
        #
        self.is_valid = True

    def __str__(self):
        """
        Returns a string representation of the current configuration object.

        Returns
        -------
        str
        """
        return str(self.__dict__)

    def __repr__(self):
        """
        self.__str__ alias to cover all cases (ex: printing an object containing a SnekConfig).

        Returns
        -------
        str
        """
        return self.__str__()

    def to_dict(self):
        """
        Returns a dict version of the current configuration.

        Returns
        -------
        dict
        """
        return self.__dict__

#-------------------------------------------------------------------------------
# Custom snekceptions
#-------------------------------------------------------------------------------
class Error(Exception):
    """Base class for exceptions in this module."""

class BuildFolderNotFound(Error):
    """Raised when the build folder cannot be reached."""

class ContentFolderNotFound(Error):
    """Raised when the content folder cannot be reached."""

class InvalidPath(Error):
    """Raised when one of the provided path is not valid."""
