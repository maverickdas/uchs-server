'''
File: uchs_exceptions.py
Project: UCHS
File Created: Monday, 27th April 2020 8:12:54 pm
Author: Abhirup Das (abhidash@outlook.com, https://github.com/maverickdas)
-----
Last Modified: Thursday, 18th June 2020 10:26:43 am
Modified By: Abhirup Das (abhidash@outlook.com, https://github.com/maverickdas)
-----
An Effort By: Team A.V.A.A.S., 2020
'''
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