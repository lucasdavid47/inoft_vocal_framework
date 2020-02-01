from inoft_vocal_framework.safe_dict import SafeDict
from json import loads as json_loads


class NestedObjectToDict:
    @staticmethod
    def _remove_start_underscores_from_string_key(string_key: str) -> str:
        index_first_underscore = None
        for i_char in range(len(string_key)):
            if string_key[i_char] == "_":
                if index_first_underscore is None:
                    index_first_underscore = i_char
            else:
                if index_first_underscore is not None:
                    cleaned_string_key = string_key[:index_first_underscore] + string_key[i_char:]
                    return cleaned_string_key
                else:
                    return string_key
        return string_key

    @staticmethod
    def _is_object_empty(class_object) -> bool:
        functions_of_object = dir(class_object)
        # We use dir and not vars, because vars do not include the functions of the class

        if "is_not_usable" in functions_of_object:
            # We make sure that the is_not_usable var is a function that can be called and not a shadow variable
            if class_object.is_not_usable():
                return True
        return False

    @staticmethod
    def _process_potential_nested_object(class_object, key_names_identifier_objects_to_go_into: list, is_first_parent_object=False) -> dict:
        for accepted_parent_key_name in key_names_identifier_objects_to_go_into:
            if hasattr(class_object, accepted_parent_key_name):
                output_dict = dict()
                keys_to_pop_after_loop_finished = list()

                main_vars_dict = vars(class_object)
                if isinstance(main_vars_dict, dict):
                    for main_var_key, main_var_object in main_vars_dict.items():
                        found_accepted_key_name_in_vars_of_current_object = False

                        for accepted_child_key_name in key_names_identifier_objects_to_go_into:
                            if hasattr(main_var_object, accepted_child_key_name):
                                found_accepted_key_name_in_vars_of_current_object = True

                                is_main_var_object_empty = NestedObjectToDict._is_object_empty(class_object=main_var_object)
                                # We remove an object that is defined as empty (see the called function for details)
                                if is_main_var_object_empty:
                                    keys_to_pop_after_loop_finished.append(main_var_key)
                                else:
                                    nested_object_accepted_key_value = getattr(main_var_object.__class__, accepted_child_key_name)
                                    cleaned_key = NestedObjectToDict._remove_start_underscores_from_string_key(nested_object_accepted_key_value)

                                    output_dict[cleaned_key] = NestedObjectToDict._process_potential_nested_object(
                                        class_object=main_var_object, key_names_identifier_objects_to_go_into=key_names_identifier_objects_to_go_into)

                                # The loop we are currently in is just to see if the object has the attribute that tell use that it is an object
                                # to go deeper into. If we found at least one, we do not need to look at the same object a second time.
                                break

                        if found_accepted_key_name_in_vars_of_current_object is False and main_var_object is not None:
                            current_item_is_not_usable = False

                            if isinstance(main_var_object, str):
                                if main_var_object.replace(" ", "") == "":
                                    current_item_is_not_usable = True

                            elif isinstance(main_var_object, dict) or isinstance(main_var_object, list):
                                if not len(main_var_object) > 0:
                                    current_item_is_not_usable = True

                            if not current_item_is_not_usable:
                                cleaned_key = NestedObjectToDict._remove_start_underscores_from_string_key(main_var_key)
                                output_dict[cleaned_key] = main_var_object

                for key_to_pop in keys_to_pop_after_loop_finished:
                    # We pop the keys after the loop has finished, to avoid
                    # issues while modifying the dict items during the loop.
                    main_vars_dict.pop(key_to_pop)

                if not is_first_parent_object:
                    return output_dict
                else:
                    parent_object_accepted_key_value = getattr(class_object.__class__, accepted_parent_key_name)
                    cleaned_parent_key = NestedObjectToDict._remove_start_underscores_from_string_key(parent_object_accepted_key_value)
                    return {cleaned_parent_key: output_dict}

    @staticmethod
    def get_dict_from_nested_object(object_to_process, key_names_identifier_objects_to_go_into: list) -> dict:
        if isinstance(key_names_identifier_objects_to_go_into, str):
            key_names_identifier_objects_to_go_into = [key_names_identifier_objects_to_go_into]

        output_dict = NestedObjectToDict._process_potential_nested_object(class_object=object_to_process,
           key_names_identifier_objects_to_go_into=key_names_identifier_objects_to_go_into, is_first_parent_object=True)
        if not isinstance(output_dict, dict):
            raise Exception(f"The following nested object converted to a dict was not of type dict but of type {type(output_dict)}")

        print(output_dict)
        return output_dict

    @staticmethod
    def process_and_set_json_request_to_object(object_class_to_set_to, request_json_dict_or_stringed_dict, key_names_identifier_objects_to_go_into: list):
        if isinstance(request_json_dict_or_stringed_dict, dict):
            request_dict = request_json_dict_or_stringed_dict
        elif isinstance(request_json_dict_or_stringed_dict, str):
            request_dict = NestedObjectToDict.get_dict_from_json(stringed_json_dict=request_json_dict_or_stringed_dict)
        else:
            raise Exception(f"The request_json_dict_or_stringed_dict variable is of type {type(request_json_dict_or_stringed_dict)} but must be dict or str.")

        unprocessed_vars_dict = vars(object_class_to_set_to)
        vars_safedict_key_processed_keys_names_with_value_unprocessed_variables_names = SafeDict()
        for key_unprocessed_var in unprocessed_vars_dict.keys():
            processed_current_key_name = NestedObjectToDict.get_json_key_from_variable_name(variable_name=key_unprocessed_var)
            vars_safedict_key_processed_keys_names_with_value_unprocessed_variables_names.put(dict_key=processed_current_key_name, value_to_put=key_unprocessed_var)

        keys_to_pop_after_loop_finished = list()
        for key_request_element, value_request_element in request_dict.items():
            current_unprocessed_variable_name = vars_safedict_key_processed_keys_names_with_value_unprocessed_variables_names.get(key_request_element).to_any()
            if current_unprocessed_variable_name is not None:
                current_child_element_object = unprocessed_vars_dict[current_unprocessed_variable_name]

                if current_child_element_object is not None:
                    found_accepted_key_name_in_vars_of_current_object = False
                    if isinstance(value_request_element, dict):

                        for accepted_child_key_name in key_names_identifier_objects_to_go_into:
                            if hasattr(current_child_element_object, accepted_child_key_name):
                                found_accepted_key_name_in_vars_of_current_object = True

                                NestedObjectToDict.process_and_set_json_request_to_object(
                                    object_class_to_set_to=unprocessed_vars_dict[current_unprocessed_variable_name],
                                    request_json_dict_or_stringed_dict=value_request_element,
                                    key_names_identifier_objects_to_go_into=key_names_identifier_objects_to_go_into)

                    if not found_accepted_key_name_in_vars_of_current_object:
                        current_item_is_not_usable = False

                        if isinstance(value_request_element, str):
                            if value_request_element.replace(" ", "") == "":
                                current_item_is_not_usable = True

                        elif isinstance(value_request_element, dict) or isinstance(value_request_element, list):
                            if not len(value_request_element) > 0:
                                current_item_is_not_usable = True

                        if not current_item_is_not_usable:
                            unprocessed_vars_dict[current_unprocessed_variable_name] = value_request_element

        for key_to_pop in keys_to_pop_after_loop_finished:
            unprocessed_vars_dict.pop(key_to_pop)

    @staticmethod
    def get_dict_from_json(stringed_json_dict: str) -> dict:
        return json_loads(stringed_json_dict)

    @staticmethod
    def get_json_key_from_variable_name(variable_name: str):
        return NestedObjectToDict._remove_start_underscores_from_string_key(variable_name)

