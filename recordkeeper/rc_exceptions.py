class RecordKeeperException(Exception):
    """ Generic exception for RecordKeeper
    """
    exception_fire = True

class RequiredField(RecordKeeperException):
    """ You can't move your king into check,
    nor can you leave your king in check 
    """
    exception_fire = True

class NoRecordsFound(RecordKeeperException):
    """ No records found matching query
    """    
    exception_fire = True

class EmptyField(RecordKeeperException):
    """ The field is empty
    """
    exception_fire = True

class InvaildRelationship(RecordKeeperException):
    """ A relationship that is not valid
    """
    exception_fire = True

class InvaildQuery(RecordKeeperException):
    """ A relationship that is not valid
    """
    exception_fire = True

class MissingRequiredInformaton(RecordKeeperException):
    """ The importer requires more information than you gave it
    """
    exception_fire = True

class DuplicateRecord( RecordKeeperException):
    """ Tried to completed an action that would result in a duplicate Record.
    """
    exception_fire = True