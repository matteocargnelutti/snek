"""
snek.snek.py Module: Main Snek class
"""
#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
import os
import glob
import datetime
from pathlib import Path
from shutil import rmtree
from distutils.dir_util import copy_tree

import markdown
import sass
import frontmatter
from mako.template import Template 
from mako.lookup import TemplateLookup

from snek.snekconfig import SnekConfig

#-------------------------------------------------------------------------------
# Main Snek class
#-------------------------------------------------------------------------------
class Snek:
    """
    Main Snek class.
    Takes configuration as a param and allows for building the site.

    Attributes
    ----------
    config: SnekConfig
        Optional configuration object, replacing the default one.
    data: dict
        Data to be shared accross templates, coming from the project's data folder (see config).
    sitemap: dict
        Content tree with meta data, parsed from the project's content folder (see config).
    sitemap_flat: list
        Simple list of filepaths from the project's content folder (see config).
    templates: list
        List of template files coming from the projects templates folder (see config).
    templates_default: str
        Path to the default template.
    build_start: datetime.datetime
        Indicates when the build started
    build_end: datetime.datetime
        Incidates when the build ended
    pages_build: int
        Indicates how many pages were built
    pages_skipped: int
        Indicates how many pages were skipped (errors)
    errors: list
        Collects build errors.

    Usage
    -----
    website = Snek()
    website.build()
    """

    def __init__(self, config=None):
        """
        Instanciates the main Snek object.

        Parameters
        ----------
        config: SnekConfig (optional)
            Replaces the default config with a specific one. Has to be of type SnekConfig.

        Returns
        -------
        Snek
        """
        # Base attributes
        self.errors = []
        self.build_start = None
        self.build_end = None
        self.pages_built = 0
        self.pages_skipped = 0
        self.data = {}
        self.sitemap = {}
        self.sitemap_flat = []
        self.templates = []
        self.templates_default = None
        self.config = None

        #
        # Check configuration object.
        #
        self.config = config

        if self.config is not None and type(self.config) is not SnekConfig:
            raise InvalidConfig(f'{type(self.config)} provided, SnekConfig expected.')

        if self.config is None:
            self.config = SnekConfig()

        if not self.config.is_valid:
            raise InvalidConfig(f'The provided configuration object is not valid.')

        #
        # Load shared data
        #
        self.__load_data()

        #
        # Load content map
        #
        self.__load_sitemap()

        #
        # Load templates list
        #
        self.__load_templates()

    def __add_error(self, message):
        """
        Add an error to the error stack.

        Parameters
        ----------
        message: string

        Returns
        -------
        tuple (datetime, message)
        """
        now = datetime.datetime.now()
        self.errors.append((now, message))
        return (now, message)

    def _find_files(self, base_path, extra_suffix=None):
        """
        Helper function to find files matching the allowed suffixes in the base_path.

        Parameters
        -----
        base_path: str
        extra_suffix: str

        Notes
        -----
        If set and starts with '.', extra_suffix will be appended to the glob pattern.
        If a file cannot be read, it will be skipped.

        Returns
        -------
        list
        """

        glob_pattern = "**/*"

        if extra_suffix and extra_suffix.startswith('.'):
            glob_pattern = f"{glob_pattern}{extra_suffix}"

        return [
            p.resolve()
            for p in Path(base_path).glob(glob_pattern)
            if (
                any([suffix in self.config.handlers for suffix in p.suffixes])
                and p.is_file()
                and os.access(p, os.R_OK)
            )
        ]

    def __parse_frontmatter_from_filepath(self, filepath, metadata_only=False):
        """
        Gets frontmatter data from filepath. If metadata_only is set and True, returns only FM metadata.

        Parameters
        -----
        filepath: path-like object

        Notes
        -----
        Returns None if the frontmatter module used a handler not allowed in self.config.handlers.
        

        Returns
        -------
        dict
        """

        fm_data = frontmatter.load(filepath)
        allowed_handlers = tuple(h['frontmatter_handler'] for h in self.config.handlers.values())
        if not isinstance(fm_data.handler, allowed_handlers):
            self.__add_error(f"{filepath} has invalid frontmatter data.")
            return None

        if metadata_only:
            return fm_data.metadata
        else:
            return fm_data

    def __parse_data_from_filepath(self, filepath):
        """
        Gets data from filepath.

        Parameters
        -----
        filepath: Path object

        Notes
        -----
        Tries to load the handler associated with the file suffix in self.config.handlers.

        Returns
        -------
        dict
        """

        # Dynamic parsing based on suffix
        file_suffix = filepath.suffix

        # Check we can load the file - this should never happen
        if file_suffix not in self.config.handlers:
            self.__add_error(f"Unknown suffix {file_suffix} for {filepath}.")
            return None

        handler = self.config.handlers[file_suffix]

        try:
            # Read and parse content
            with open(filepath, "r") as fp:
                data_piece = handler['loader'](fp)
        # If the file's content is not valid
        except handler['exception'] as err:
            self.__add_error(f"{filepath} does not contain valid data: {err}")
            return None

        return data_piece

    def __get_nested_keys_from_filepath(self, filepath, base_path):
        """
        Strips base_path from filepath, and returns the path as a list of strings.
        The list can be used to update a "nested" dictionary.

        Parameters
        -----
        filepath: Path object
        base_path: Path object

        Notes
        -----
        Removes the suffixes - expects at most 2 suffixes (allowed suffix + extra suffix).
        (.json.md, .yml.md)

        Returns
        -------
        dict
        """

        # Turns into a relative path
        relative_path = filepath.relative_to(Path(base_path).resolve())

        # Get all but the last element
        keys = str(relative_path).split('/')[:-1]
        
        # Gets the last element
        final_key = relative_path.stem
        
        # It could still have a suffix (.json.md): strip it
        if final_key.endswith(tuple(self.config.handlers.keys())):
            final_key, _ = os.path.splitext(final_key)

        # Add the last element
        keys.append(final_key)

        return keys
        
    def __update_data_from_filepath(self, filepath):
        """
        Updates self.data with data from file.

        Parameters
        -----
        filepath: Path object

        Returns
        -------
        None
        """

        base_path = self.config.data_path
        nested_keys = self.__get_nested_keys_from_filepath(filepath, base_path)
 
        data = self.__parse_data_from_filepath(filepath)
        self.__update_attr_from_nested_keys(self.data, nested_keys, data)

    def __update_sitemap_from_filepath(self, filepath):
        """
        Updates self.sitemap with metadata from file.

        Parameters
        -----
        filepath: Path object

        Returns
        -------
        None
        """

        base_path = self.config.content_path
        nested_keys = self.__get_nested_keys_from_filepath(filepath, base_path)

        data = self.__parse_frontmatter_from_filepath(filepath, metadata_only=True)

        # Defaults for metadata
        metadata = {
            'filepath': str(filepath),
            'title': '',
            'template': None,
            'category': None,
            'tags': [],
            'date': None
        }
        # We don't want a rogue filepath from metadata
        data.pop("filepath", None)
        
        # Updates the default values
        metadata.update(data)

        self.__update_attr_from_nested_keys(self.sitemap, nested_keys, metadata)

    def __update_attr_from_nested_keys(self, attr, keys, value):
        """
        Updates the dictionary `attr`. Creates / updates nested dictionaries based on the `keys`.
        `value` is the last "child".
        nested_keys = ('content', 'dir1', 'subfolder', 'my_file')
        -> attr['content']['dir1']['subfolder']['my_file'] = value

        Parameters
        -----
        attr: dict
        keys: list
        value: object

        Returns
        -------
        None
        """
        
        if not keys:
            return None

        branch = attr

        # Traverse the dictionary through all but the last nested key
        for k in keys[:-1]:
            if not k in branch:
                branch[k] = {}
            branch = branch[k]

        # Updates the last leaf
        if keys[-1] not in branch:
            branch[keys[-1]] = value
        # Unless there is already something there
        else:
            self.__add_error(f"{os.path.join(*keys)} conflicts with another item.")
        
    def __load_data(self):
        """
        Loads data to be shared accross templates into self.data.

        Notes
        -----
        - Wipes the previous self.data if everything goes through

        Returns
        -------
        bool
        """
        
        # Collect all files from the data folder
        data_filepaths = self._find_files(self.config.data_path)

        # Clear self.data
        self.data = {}

        # For each file, load and parse content
        for filepath in data_filepaths:
            self.__update_data_from_filepath(filepath)


    def __load_templates(self):
        """
        List all templates files in self.templates

        Returns
        -------
        bool
        """
        # Load all template files
        self.templates = glob.glob(f"{self.config.templates_path}/**/*.html", recursive=True)

        # Check if the default is available
        has_default_template = False

        for template in self.templates: # Look for a "index.html" at the root of the templates folder
            template_check = template.replace(self.config.templates_path, '')
            template_check = template_check.replace('/', '')
            template_check = template_check.replace('\\', '')

            if template_check == 'index.html':
                has_default_template = True
                self.templates_default = template # Remember the default template

        if not has_default_template:
            raise NoDefaultTemplate

        # If we land here, there is at least the default template.
        return True

    def __load_sitemap(self):
        """
        List all content files and load their metadata in self.sitemap and self.sitemap_flat

        Returns
        -------
        bool
        """
        # Clear sitemap
        self.sitemap = {}
        self.sitemap_flat = []

        filepaths = self._find_files(self.config.content_path, extra_suffix=".md")

        # For each file, parse metadata and add to sitemap
        for filepath in filepaths:
            # Add entry to sitemap_flat
            self.sitemap_flat.append(str(filepath))
            # Update self.sitemap
            self.__update_sitemap_from_filepath(filepath)

        return True

    def build(self):
        """
        Initiates a build:
        - Wipes the current build folder
        - Build assets files
        - Processes content files

        Returns
        -------
        bool
        """
        # Timer start
        self.pages_built = 0
        self.pages_skipped = 0
        self.build_start = datetime.datetime.now()

        # Build assets files and JavaScript
        self.__build_assets()
        self.__build_js()

        # Build scss if option active
        if self.config.scss_active:
            self.__build_scss()
        # Build css if scss option inactive
        else:
            self.__build_css()

        # Process content files
        self.__build_content()

        # Copy data files if asked to in config
        if self.config.data_in_build:
            self.__build_data()

        # Timer end
        self.build_end = datetime.datetime.now()

        return True

    def get_build_report(self):
        """
        Returns stats as a dict.

        Returns
        -------
        dict
        """
        return {
            'build_start': self.build_start,
            'build_end': self.build_end,
            'build_time': self.build_end - self.build_start,
            'pages_built': self.pages_built,
            'pages_skipped': self.pages_skipped,
            'errors': self.errors
        }

    def __build_content(self):
        """
        Processes content files: generates HTML by running them through their associated template.

        Templates have access to the following variables:
        -------------------------------------------------
        - metadata: front matter from the content file
        - content: Parsed markdown from the content file
        - data: Shared data from the project's data folder
        - sitemap: complete sitemap
        - config: current configuration as a dict

        Returns
        -------
        bool
        """
        # For each content file
        for source_filepath in self.sitemap_flat:

            # Read and parse content
            page = self.__parse_frontmatter_from_filepath(source_filepath)

            # Check we parsed successfully
            if not page.metadata:
                self.pages_skipped += 1
                continue

            # In the content filepath, replace content source folder by build folder
            destination_filepath = source_filepath.replace(self.config.content_path, self.config.build_path)
            
            # Then strip the final .md
            destination_filepath = destination_filepath.replace('.md', '')
            
            # Strip the extension if it is valid
            if destination_filepath.endswith(tuple(self.config.handlers.keys())):
                destination_filepath, _ = os.path.splitext(destination_filepath)

            destination_filepath = f"{destination_filepath}.html"

            # Determine which template should be used.
            # If content has a "template" field, check it is valid and use it.
            template_filepath = self.templates_default

            if 'template' in page.metadata and page.metadata['template']:

                # Append the template folder to the provided template value
                wanted_template = f"{self.config.templates_path}/{page.metadata['template']}"

                # And check if it exists
                if os.path.exists(wanted_template):
                    template_filepath = wanted_template

            #
            # Render content using template into HTML file
            #

            # Parse markdown
            page.content = markdown.markdown(page.content)

            # Render template
            lookup = TemplateLookup(directories=[self.config.templates_path,]) # Used to make the template aware of its suroundings
            renderer = Template(filename=template_filepath, lookup=lookup)
            html = renderer.render(data=self.data,
                                    sitemap=self.sitemap,
                                    config=self.config.__dict__,
                                    metadata=page.metadata,
                                    content=page.content)

            # Write HTML file
            destination_dirname = os.path.dirname(destination_filepath)
            if not os.path.exists(destination_dirname):
                os.makedirs(destination_dirname)

            open(destination_filepath, 'w').write(html)

            # Count as built
            self.pages_built += 1


    def __build_scss(self):
        """
        Builds content of SCSS files to the /css folder of the build folder.
        Will be ignored if config.scss_active is False.

        Returns
        -------
        bool
        """
        input_folder = self.config.scss_path
        output_folder = self.config.build_path+'/css'
        scss_output_style = self.config.scss_output_style

        sass.compile(dirname=(input_folder, output_folder), output_style=scss_output_style)

        return True

    def __build_css(self):
        """
        Copies contents of the CSS folder to /css in the build folder.
        Will be ignored by build() if config.scss_active is True.

        Returns
        -------
        bool
        """
        copy_tree(self.config.css_path, self.config.build_path + '/css')
        return True

    def __build_js(self):
        """
        Copies contents of the JavaScript folder to /js in the build folder

        Returns
        -------
        bool
        """
        copy_tree(self.config.js_path, self.config.build_path + '/js')
        return True

    def __build_data(self):
        """
        Copies contents of the data folder to /__data in the build folder.
        Will be ignored by build() if config.data_in_build is False.

        Returns
        -------
        bool
        """
        copy_tree(self.config.data_path, self.config.build_path + '/__data')
        return True

    def __build_assets(self):
        """
        Copies contents of the assets folder to /assets in the build folder

        Returns
        -------
        bool
        """
        copy_tree(self.config.assets_path, self.config.build_path + '/assets')
        return True

#-------------------------------------------------------------------------------
# Custom snekceptions
#-------------------------------------------------------------------------------
class Error(Exception):
    """Base class for exceptions in this module."""

class InvalidConfig(Error):
    """Raised when the provided configuration object is not valid."""

class NoDefaultTemplate(Error):
    """Raised when no default template was found (index.html)."""
