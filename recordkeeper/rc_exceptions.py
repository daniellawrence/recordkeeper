class RecordKeeperException(Exception):
    """ Generic exception for RecordKeeper
    """

class RequiredField(RecordKeeperException):
    """ You can't move your king into check,
    nor can you leave your king in check 
    """
    
class NoRecordsFound(RecordKeeperException):
    """ No records found matching query
    """    

class EmptyField(RecordKeeperException):
    """ The field is empty
    """

class InvaildRelationship(RecordKeeperException):
    """ A relationship that is not valid
    """

class InvaildQuery(RecordKeeperException):
    """ A relationship that is not valid
    """

class MissingRequiredInformaton(RecordKeeperException):
    """ The importer requires more information than you gave it
    """

class DuplicateRecord( RecordKeeperException):
    """ Tried to completed an action that would result in a duplicate Record.
    """