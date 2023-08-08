FILE_TYPES = [
    'csv', 'cvs', # typo
]
U16_MAX = 2**16 - 1

from typing import Optional, Dict, Any, List
import csv

ConfigDict = Dict[str, Any]

def _parse_config_from_csv_dict(file_rows: Dict[str, Any]) -> ConfigDict:
    config_dict: ConfigDict = {}

    for row in file_rows:
        config_dict[row['key']] = row['value']

    return config_dict


def _read_file(file_path: str) -> List[str]:
    with open(file_path, 'r') as f:
        return f.readlines()

def _read_csv_file(file_path: str) -> ConfigDict:
    file_contents: List[str] = _read_file(file_path)
    csv_reader = csv.DictReader(file_contents) # uses first row as keys
    rows = list(csv_reader)
    
    return _parse_config_from_csv_dict(rows)

def _parse_config_from_file(file_path: str, file_type: Optional[str] = None) -> ConfigDict:
    if file_type is None:
        file_type = file_path.split('.')[-1].lower()

    if file_type not in FILE_TYPES:
        raise ValueError(f"Unsupported file type: {file_type}")

    try:
        if file_type in ['csv', 'cvs']:
            return _read_csv_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    except FileNotFoundError as e:
        raise ValueError(f"File not found: {file_path}: Error: {e}")
    
def _validate_stratum_url(url: str) -> None:
    # Should NOT include protocol
    if '://' in url:
        raise ValueError(f"Stratum url should not include protocol: {url}")
    
    # Should NOT include port
    ## CAN be IPv6
    _, separator, _ = url.rpartition(':')
    if separator == ':':
        raise ValueError(f"Stratum url should not include port: {url}")

def _check_stratum_url(field, value, error) -> None:
    try:
        _validate_stratum_url(value)
    except ValueError as e:
        error(field, str(e))


def validate_config(config_path: str) -> None:
    parsed_config = _parse_config_from_file(config_path)

    import cerberus
    schema = {
        'wifissid': {
            'type': 'string',
            'required': True,
        },
        'wifipass': {
            'type': 'string',
            'required': True,
        },
        'stratumurl': {
            'type': 'string',
            'check_with': _check_stratum_url, # custom validate function
            'required': True,
        },
        'stratumport': {
            'type': 'integer',
            'coerce': int,
            'min': 0,
            'max': U16_MAX,
            'required': True,
        },
        'stratumuser': {
            'type': 'string',
            'required': True,
        },
        'stratumpass': {
            'type': 'string',
            'required': True,
        },
        'bm1397frequency': {
            'type': 'integer',
            'coerce': int,
            'min': 0,
            'max': U16_MAX,
            'required': True,
        },
        'bm1397voltage': {
            'type': 'integer',
            'coerce': int,
            'min': 0,
            'max': U16_MAX,
            'required': True,
        },
    }
    v = cerberus.Validator(schema, allow_unknown=True)
    if not v.validate(parsed_config):
        raise ValueError(v.errors)



def check_validate_dependencies() -> Optional[str]:
    try:
        import cerberus
    except ImportError:
        return \
        """The --validate_config option requires the cerberus package.
        Install it with: pip install cerberus or pip install bitaxetool[validate]
        """

    return None
