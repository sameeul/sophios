"""CWL Types."""
from enum import Enum
from pathlib import Path
from typing import Any


class CWLTypesEnum(str, Enum):
    NULL = "null"
    BOOLEAN = "boolean"
    INT = "int"
    LONG = "long"
    FLOAT = "float"
    DOUBLE = "double"
    STRING = "string"
    FILE = "File"
    DIRECTORY = "Directory"


class ScatterMethod(Enum):
    dotproduct = "dotproduct"
    flat_crossproduct = "flat_crossproduct"
    nested_crossproduct = "nested_crossproduct"
