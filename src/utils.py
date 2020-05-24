from uuid import UUID
import uchs_exceptions as exs


def is_valid_uuid(string, version_num=1):
    assert version_num <= 4, "UUID versions upto 4 supported"
    try:
        val = UUID(string, version=version_num)
    except ValueError:
        return False
    return val.hex == string
