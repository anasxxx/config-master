from enum import Enum

class State(str, Enum):
    COLLECT = "collect"
    VALIDATE = "validate"
    ENRICH = "enrich"
    GENERATE_XML = "generate_xml"
    DONE = "done"
    ERROR = "error"
