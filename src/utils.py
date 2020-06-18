'''
File: utils.py
Project: UCHS
File Created: Sunday, 31st May 2020 5:05:30 pm
Author: Abhirup Das (abhidash@outlook.com, https://github.com/maverickdas)
-----
Last Modified: Thursday, 18th June 2020 10:27:48 am
Modified By: Abhirup Das (abhidash@outlook.com, https://github.com/maverickdas)
-----
An Effort By: Team A.V.A.A.S., 2020
'''
from uuid import UUID
import uchs_exceptions as exs


def is_valid_uuid(string, version_num=1):
    assert version_num <= 4, "UUID versions upto 4 supported"
    try:
        string  = "".join(string.split("-"))
        print(string)
        val = UUID(string, version=version_num)
    except ValueError:
        return False
    return val.hex == string


def byte_to_int(byte_var):
    return int.from_bytes(byte_var, byteorder="big")
