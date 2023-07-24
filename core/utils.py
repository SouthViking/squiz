import humps
import configparser
from typing import List, Any, Dict

def get_empty_entries(object: dict, target_keys: List[str]) -> List[str]:
    empty_entries = []
    for key in target_keys:
        if key not in object:
            empty_entries.append(key)
            continue
        if type(object[key]) == str and len(object[key].strip()) == 0:
            empty_entries.append(key)
            continue

    return empty_entries

def camelize_list(elements: List[str]):
    for i in range(len(elements)):
        elements[i] = humps.camelize(elements[i])


def get_config_values_from_file(filepath: str, section_name: str) -> Dict[str, Any]:
    try:
        config = configparser.RawConfigParser()
        config.read(filepath)

        return dict(config.items(section_name))
    except Exception as error:
        print(error)

        return {}
