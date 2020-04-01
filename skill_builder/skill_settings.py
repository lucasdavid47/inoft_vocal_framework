import os
from pathlib import Path
from typing import Tuple, Optional, Any

import click
from cerberus import Validator
from inoft_vocal_framework.safe_dict import SafeDict


class Settings:
    _settings = None
    settings_loaded = False
    last_settings_filepath = None
    last_settings_file_extension_type = None

    class ExtendedValidator(Validator):
        def _validate_check_database_field_present(self, check_database_field_present: bool, field: str, value):
            """ {'type': 'boolean'} """
            if check_database_field_present is True and value not in self.document.keys():
                self._error(field, f"The key {value} was missing from the following section : {self.document}")

        def _validate_is_database_not_disabled(self, is_database_not_disabled: bool, field: str, value):
            """ {'type': 'boolean'} """
            if is_database_not_disabled is True and "disable_database" in self.document.keys() and self.document["disable_database"]:
                self._error(field, f"The database is disabled in the following section : {self.document}")

    @property
    def _settings_file_validator_schema(self) -> dict:
        return {
            "default_session_data_timeout": {
                "required": True,
                "type": "integer"
            },
            "sessions_users_data": {
                "required": True,
                "type": "dict",
                "schema": {
                    "disable_database": {
                        "required": False,
                        "type": "boolean",
                    },
                    "database_client": {
                        "required": True,
                        "type": "string",
                        "allowed": ["dynamodb"],
                        "is_database_not_disabled": True,
                        "check_database_field_present": True,
                    },
                    "dynamodb": {
                        "type": "dict",
                        "schema": {
                            "table_name": {
                                "required": True,
                                "type": "string"
                            },
                            "region_name": {
                                "required": True,
                                "type": "string"
                            }
                        }
                    }
                }
            },
            "messages": {
                "required": True,
                "type": "dict",
                "schema": {
                    "use_database_dynamic_messages": {
                        "required": True,
                        "type": "boolean"
                    },
                    "database_client": {
                        "type": "string",
                        "allowed": ["dynamodb"],
                        "required": True,
                        "check_database_field_present": True,
                        "dependencies": {"use_database_dynamic_messages": True}
                    },
                    "dynamodb": {
                        "type": "dict",
                        "schema": {
                            "table_name": {
                                "required": True,
                                "type": "string"
                            },
                            "region_name": {
                                "required": True,
                                "type": "string"
                            }
                        }
                    }
                }
            },
            "deployment": {
                "required": True,
                "type": "dict",
                "schema": {
                    "api_gateway_id": {
                        "type": "string",
                    }
                }
            }
        }

    @property
    def settings(self) -> SafeDict:
        if Settings.settings_loaded is not True:
            raise Exception(f"The settings have not yet been loaded and are : {Settings.settings}")
        return Settings._settings

    @settings.setter
    def settings(self, settings_dict: dict):
        validator = self.ExtendedValidator()
        is_valid = validator.validate(settings_dict, self._settings_file_validator_schema)
        if is_valid is not True:
            raise Exception(f"The settings file was not valid. Please modify it or recreate it : {validator.errors}")
        else:
            Settings._settings = SafeDict(settings_dict)
            Settings.settings_loaded = True

    def find_load_settings_file(self, root_folderpath: str):
        def list_settings_filepaths(dirpath: str) -> list:
            found_settings_filepaths = []
            for root_dirpath, dirs, filenames in os.walk(dirpath):
                if "\\inoft_vocal_framework\\templates" not in root_dirpath:
                    # The app_settings file of the templates of the framework
                    # are not considered as valid app_settings file.
                    for filename in filenames:
                        if Path(filename).stem == "app_settings":
                            found_settings_filepaths.append(os.path.join(root_dirpath, filename))
            return found_settings_filepaths

        found_files = list_settings_filepaths(root_folderpath)

        file_path_object = None
        while file_path_object is None:
            print(f"Found {len(found_files)} settings file at following paths :")
            for i_file, file in enumerate(found_files):
                print(f"{i_file + 1} - {file}")
            file_index = str(click.prompt("What is the number of the file you wish to use ?"))
            if not file_index.isdigit() or int(file_index) > len(found_files) or int(file_index) < 0:
                print("Please write a valid file index in the form of an int like 1 or 3")
            else:
                selected_filepath = found_files[int(file_index) - 1]
                print(f"Selected settings filepath : {click.style(text=selected_filepath, fg='blue')}")
                file_path_object = Path(selected_filepath)


        if file_path_object.suffix == ".yaml":
            self.load_yaml(file_path_object)
        elif file_path_object.suffix == ".json":
            self.load_json(file_path_object)
        else:
            raise Exception(f"The only supported settings file extension are .yaml and"
                            f" .json but your file was in {file_path_object.suffix}")

    def load_yaml(self, settings_file: str):
        from yaml import safe_load, YAMLError
        with open(settings_file, "r") as file_stream:
            try:
                self.settings = safe_load(file_stream)
            except YAMLError as error:
                raise Exception(f"The yaml file was not valid, and caused an error when loading."
                                f"Please check the file or recreate it with the cli : {error}")
        Settings.last_settings_filepath = settings_file
        Settings.last_settings_file_extension_type = "yaml"

    def load_json(self, settings_file: str):
        from json import load as json_load
        with open(settings_file, "r") as file_stream:
            try:
                self.settings = json_load(file_stream)
            except Exception as error:
                raise Exception(f"The json file was not valid, and caused an error when loading."
                                f"Please check the file or recreate it with the cli : {error}")
        Settings.last_settings_filepath = settings_file
        Settings.last_settings_file_extension_type = "json"

    def save_settings(self):
        from json import dumps as json_dumps
        from yaml import safe_dump as yaml_dump

        if Settings.last_settings_file_extension_type in ["yaml", "json"]:
            settings_dict = self.settings.to_dict()

            with open(Settings.last_settings_filepath, "w+") as file_stream:
                settings_dict = self.settings.to_dict()
                file_stream.write(yaml_dump(settings_dict) if Settings.last_settings_file_extension_type == "yaml" else json_dumps(settings_dict))
        else:
            raise Exception("Please load a valid yaml or json settings file before attempting to save them.")
