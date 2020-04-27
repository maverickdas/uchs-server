class Errors(Exception):
    """Base class for other exceptions"""
    pass
class ObjError(Errors):
    """Raised when objects fails to be initialised/ configured"""
    pass
class DBError(Errors):
    """Raised when DB operations fail"""
    pass
class DevError(Errors):
    """Raised when dev code/algo is flawed"""
    pass