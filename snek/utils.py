import os
from pathlib import Path


class SnekUtils:
    @staticmethod
    def find_files(where, suffixes=None, extra_suffix=""):
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

        if suffixes is None:
            suffixes = list()

        glob_pattern = f"**/*"

        if extra_suffix:
            glob_pattern = f"{glob_pattern}{extra_suffix}"

        # Find files
        paths = Path(where).glob(glob_pattern)

        # Filter function - can we read the file?
        is_readable = lambda p: p.is_file() and os.access(p, os.R_OK)

        # Filter function
        # Does the file have any suffix that matches the ones allowed in the config?
        has_valid_suffixes = lambda p: any(
            [suffix in suffixes for suffix in p.suffixes]
        )

        # Combine the filters
        is_valid_path = lambda p: is_readable(p) and has_valid_suffixes(p)

        # Filter them and return a list of resolved (absolute) paths
        return [p.resolve() for p in filter(is_valid_path, paths)]


    def get_nested_keys_from_filepath(filepath, where="", strip_suffixes=None):
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

        if strip_suffixes is None:
            strip_suffixes = list()

        # Turns into a relative path
        relative_path = filepath.relative_to(Path(where).resolve())

        # Get all but the last element
        keys = str(relative_path).split(os.sep)[:-1]

        # Gets the last element without suffix
        final_key = relative_path.stem

        # It could still have a suffix (.json.md): strip it
        if final_key.endswith(tuple(strip_suffixes)):
            final_key, _ = os.path.splitext(final_key)

        # Add the last element
        keys.append(final_key)

        return keys

class SnekDict(dict):
    def update_from_nested_keys(self, keys, value):
        """
        Updates the dictionary. Creates / updates nested dictionaries based on the `keys`.
        `value` is the last "child".
        nested_keys = ('content', 'dir1', 'subfolder', 'my_file')
        -> self['content']['dir1']['subfolder']['my_file'] = value

        Parameters
        -----
        keys: list
        value: object

        Returns
        -------
        None
        """

        if not keys:
            return None

        branch = self

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
            raise DuplicateKeyError(f"{os.path.join(*keys)} conflicts with another item.")

# Custom exception
class DuplicateKeyError(KeyError):
    pass
