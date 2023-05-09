"""
The pyconfig module contains collection of
objects (DotDict + Config) which helps you
to access configurations in JSON files for
Google Cloud Platform based projects.
"""

import json
import copy
import re


class DotDict(dict):
    """
    a dictionary that supports dot notation
    as well as dictionary access notation
    usage: d = DotDict() or d = DotDict({'val1':'first'})
    set attributes: d.val2 = 'second' or d['val2'] = 'second'
    get attributes: d.val2 or d['val2']
    """

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dct):
        for key, value in dct.items():
            if hasattr(value, "keys"):
                value = DotDict(value)
            self[key] = value


def _get_attribute(obj, attr):
    """Method returns value of attribute from object in any deep level.

    :param obj: object
    :param attr: sequence of the attributes in for of string separated by dot
    :return:
    """

    if isinstance(attr, str):
        attr = attr.split(".")

    for key in attr:
        obj = getattr(obj, key)

    return obj


class Formatter:
    """Config class simplifies interaction with configuration files
    and accessing names of the services within the python scripts
    """

    def __init__(
            self,
            config: dict,
            naming_patterns: dict
    ):
        """Create instance of the Config class

        :param config: dictionary with configuration
        :type config: dict
        :param naming_patterns: dictionary with naming patterns
        :type naming_patterns: dict
        """

        self.config = DotDict(config)
        self.naming_patterns = DotDict(naming_patterns)

    @staticmethod
    def import_config(configs):
        """Method imports configuration files.

        :param configs: dictionary of config files

            {
                "project": "path/to/project/config/file.json",
                "services": "path/to/services/config/file.json",
                "solution": "path/to/solution/config/file.json",
                "tenants": "path/to/tenants/config/file.json",
            }

        :type configs: dict
        :return: dictionary with configuration
        :rtype: dict
        """

        config = {}

        for key in configs.keys():
            conf = Formatter.load_json(path=configs[key])
            if key in conf:
                config[key] = Formatter.load_json(path=configs[key]).get(key)
            else:
                config[key] = Formatter.load_json(path=configs[key])

        return config

    @staticmethod
    def load_json(path=None):
        """Method loads a json config file.

        :param path: path to the config file directory
        :type path: str
        :return: JSON as dictionary
        :rtype: dict
        """

        # exist strategy for not used config files
        with open(path, "r") as file_content:
            content = json.load(file_content)

        return content

    def get(self, pattern: str):
        """Method formats naming pattern.

        :param pattern: naming pattern
        :type pattern: str

        :example:

        >>> formatter = Formatter()
        >>> config.get(pattern="project.name")

        :return: formatted pattern
        :rtype: str
        """

        naming_pattern = self._get_config_item(name=pattern)
        naming_pattern = naming_pattern.replace("${", "{")

        config = copy.copy(self.config)

        naming_pattern, config = self.change_letter_case(
            naming_pattern=naming_pattern,
            config=config
        )
        naming_pattern, config = self.do_replace(
            naming_pattern=naming_pattern,
            config=config
        )

        return naming_pattern.format(**config)

    def _get_config_item(self, name, source="naming_patterns"):
        """Method returns config item by dotted name or list.

        :param item: naming pattern name
        :type item: list|str

        :example:

        >>> config = Config()
        >>> config._get_config_item(name="project.name")
        >>> config._get_config_item(name=["project", "name"])

        :return: config_item
        :rtype: str
        """

        if isinstance(name, str):
            item = name.split(".")
        config_item = getattr(self, source)

        for key in item:

            config_item = config_item.get(key)

            if config_item is None:
                raise KeyError(
                    f"Naming pattern key: `{key}` not found in `{config_item}`"
                )
        return config_item

    @classmethod
    def change_letter_case(cls, naming_pattern, config):

        regex = r"(?P<func>lower|upper)\((?P<arg>[^)]*)\)"

        matches = re.finditer(regex, naming_pattern)

        for match in matches:
            func_name = match.group("func")
            arg = match.group("arg")

            naming_pattern = naming_pattern.replace(
                f"{func_name}({arg})",
                arg
            )

            val = _get_attribute(obj=config, attr=arg)
            if getattr(val, func_name) is not None:
                val = getattr(val, func_name)()
                cls._set_attribute(obj=config, attr=arg, value=val)

        return naming_pattern, config

    @classmethod
    def do_replace(cls, naming_pattern, config):
        """Method replaces values in naming pattern.

        :param naming_pattern: naming pattern
        :type naming_pattern: str
        :param config: config dictionary
        :type config: dict
        """

        regex = r"(?P<func>replace)\((?P<args>[^)]*)\)"

        matches = re.finditer(regex, naming_pattern)

        for match in matches:

            func_name = match.group("func")
            args = match.group("args")
            adj_args = args.replace(", ", ",")
            var, original, new = adj_args.split(",")

            naming_pattern = naming_pattern.replace(
                f"{func_name}({args})",
                var.split(",")[0]
            )

            val = _get_attribute(obj=config, attr=var)

            if getattr(val, func_name) is not None:
                val = val.replace(
                    cls.remove_quotes(original),
                    cls.remove_quotes(new)
                )
                cls._set_attribute(obj=config, attr=var, value=val)

        return naming_pattern, config

    @staticmethod
    def _set_attribute(obj, attr, value):
        """Method sets value of attribute from object in any deep level.

        :param obj: object
        :param attr: sequence of the attributes in for of string separated by dot
        :param value: value to be set
        :return: object with set attribute
        :rtype: object
        """

        if isinstance(attr, str):
            attr = attr.split(".")

        for key in attr[:-1]:
            obj = getattr(obj, key)

        setattr(obj, attr[-1], value)

        return obj

    @staticmethod
    def remove_quotes(string):
        """Method removes quotes from string.

        :param string: string
        :type string: str
        :return: string without quotes
        :rtype: str
        """

        return string.replace('"', "").replace("'", "")
