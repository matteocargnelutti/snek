"""
snek.snek.py Module: Main Snek class
"""
#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
import os
import json
import glob
import datetime
from shutil import rmtree
from distutils.dir_util import copy_tree

import markdown
import sass
import frontmatter
from frontmatter.default_handlers import JSONHandler as frontmatter_json_handler
from mako.template import Template

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
        # Collect all json files from the data folder
        data_filepaths = glob.glob(f"{self.config.data_path}/**/*.json", recursive=True)

        # Clear self.data
        self.data = {}

        # For each file:
        # - Load and parse content content
        # - Create an entry in self.data that matches their position inside the data folder
        for filepath in data_filepaths:

            try:
                # Read and parse content
                data_piece = open(filepath).read()
                data_piece = json.loads(data_piece)

                # Remove the data folder from filepath and split it into components
                filepath = filepath.replace(f"{self.config.data_path}/", '')
                filepath_components = filepath.split(os.sep)

                # Iterate through the filepath components to add this data to a place in self.data,
                # so it matches its position in the data folder.
                # Ex: if ./data/folder1/folder2/file.json > self.data['folder1']['folder2']['file']
                branch = self.data # branch iterator through self.data
                for component in filepath_components:

                    # If we have reached the file, clean its name and add content to self.data
                    if component == filepath_components[-1]:
                        key = component.replace('.json', '')
                        branch[key] = data_piece
                        break

                    # If we have reached a directory and it does not exist a key for it in self.data, create it.
                    if component not in branch.keys():
                        branch[component] = {}

                    # Update branch iterator so we are one level deeper in self.data
                    branch = branch[component]

            # If the file could not be read or open
            except FileNotFoundError:
                self.__add_error(f"{filepath} cannot be read.")
            # If the file's content is not valid JSON
            except json.decoder.JSONDecodeError as err:
                self.__add_error(f"{filepath} does not contain valid JSON. {err}")

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

        # For each content file:
        # - Read and parse meta data
        # - Add to the sitemap tree in a way that matches the content folder structure.
        for filepath in glob.glob(f"{self.config.content_path}/**/*.json.md", recursive=True):

            # Add entry to sitemap_flat
            self.sitemap_flat.append(filepath)

            #
            # Prepare meta data
            #

            # Defaults
            metadata = {
                'filepath': filepath,
                'title': '',
                'template': None,
                'category': None,
                'tags': [],
                'date': None
            }

            # Load from front-matter and add to default
            try:
                metadata_from_file = frontmatter.load(filepath, handler=frontmatter_json_handler()).metadata
                for key, value in metadata_from_file.items():
                    metadata[key] = value

            # If the file could not be read or open, go to next file
            except FileNotFoundError:
                self.__add_error(f"{filepath} cannot be read.")
                continue
            # If the file's content is not valid JSON frontmatter, simply log it
            except json.decoder.JSONDecodeError as err:
                self.__add_error(f"{filepath} does not contain valid JSON. {err}")

            #
            # Add item and meta data to sitemap tree
            #

            # Remove the content folder from filepath and split it into componetns
            filepath = filepath.replace(f"{self.config.content_path}/", '')
            filepath_components = filepath.split(os.sep)

            # Iterate through the filepath components to add this data to a place in self.data,
            # so it matches its position in the data folder.
            # Ex: if ./content/folder1/folder2/file.json > self.sitemap['folder1']['folder2']['file']
            branch = self.sitemap # branch iterator through self.data
            for component in filepath_components:

                # If we have reached the file, clean its name and add content to self.data
                if component == filepath_components[-1]:
                    key = component.replace('.json.md', '')
                    branch[key] = metadata
                    break

                # If we have reached a directory and it does not exist a key for it in self.data, create it.
                if component not in branch.keys():
                    branch[component] = {}

                # Update branch iterator so we are one level deeper in self.data
                branch = branch[component]

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

            try:
                # Read and parse content
                page = frontmatter.load(source_filepath, handler=frontmatter_json_handler())

                # In the content filepath, replace content source folder by build folder, and replace ext .md.json by .html
                destination_filepath = source_filepath.replace(self.config.content_path, self.config.build_path)
                destination_filepath = destination_filepath.replace('.json.md', '.html')

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
                renderer = Template(filename=template_filepath)
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

            # If the file could not be read or open
            except FileNotFoundError as err:
                self.pages_skipped += 1
                self.__add_error(err)
            # If the file's content is not valid JSON
            except json.decoder.JSONDecodeError as err:
                self.pages_skipped += 1
                self.__add_error(err)

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
