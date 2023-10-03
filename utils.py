import json
import sys
from typing import Optional


class JsonHandler:
    def __init__(self):
        """
        Custom Json Handler/Helper.
        """
        self.ERROR_MESSAGE = "Failed to load {} from settings config. Make sure to add \"{}\": <{}> in the config json."

    @staticmethod
    def load_json_file(file: str) -> dict | int:
        """
        Load json from a given file path.
        :param file: Directory to file
        :return: Json Dictionary, or 1 if failed.
        """
        try:
            with open(file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return 1

    def get_element(self, json_settings: dict, settings_name: str) -> Optional[str]:
        """
        Get a setting from a dict.
        :param json_settings: The Json to get the setting from.
        :param settings_name: The Setting's name
        :return: Setting Value
        """
        settings_value = json_settings.get(settings_name, None)
        if settings_value is None:
            print(self.ERROR_MESSAGE.format(settings_name, settings_name.lower(), settings_name))
            sys.exit(1)
        return settings_value
