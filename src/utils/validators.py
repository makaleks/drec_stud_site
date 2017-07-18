import re

def _check_valid(v):
    if v.match(s) is None:
        return False
    else:
        return True


# r     - raw string (no python escape sequences like '\n')
# ^     - string begining
# $     - string end
# []    - character set
# |     - OR
# +     - one or more
# ?     - one or none
# ()    - just brackets to set priority

# Николай Андреевич Римский-Корсаков
def is_valid_name(s):
    _name_valid = re.compile(r"^([А-Я|Ё]([а-я|ё]+)([-| ]?))+$")
    return _check_valid(_name_valid)

# +79000000000
def is_valid_phone(s):
    _phone_valid = re.compile(r"^\+?[0-9]+$")
    return _check_valid(_phone_valid)

# user.web-admin@phystech.edu
def is_valid_email(s):
    _email_valid = re.compile(r"^[0-9a-z]+([-.]?[0-9a-z]+)*@[0-9a-z]+\.[a-z]+$")
    return _check_valid(_email_valid)
