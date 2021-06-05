import os
import re

from user.models import Faculty

def _check_valid(v, s):
    if (s is None) or (v.match(s) is None):
        return False
    else:
        return True


# r     - raw string (no python escape sequences like '\n')
# ^     - string beginning
# $     - string end
# []    - character set
# |     - OR
# +     - one or more
# ?     - one or none
# ()    - just brackets to set priority

# Николай Андреевич Римский-Корсаков
def is_valid_name(s):
    _name_valid = re.compile(r"^([А-Я|Ё]([а-я|ё]+)([-| ]?))+$")
    return _check_valid(_name_valid, s = s)

# +7-(900)-0(0)0-00-00
def is_valid_phone(s):
    _phone_valid = re.compile(r"^\+?[0-9](([ -]?([0-9]+|(\([0-9]+\))))+)$")
    return _check_valid(_phone_valid, s = s)

# user.web-admin@phystech.edu
def is_valid_email(s):
    _email_valid = re.compile(r"^[0-9a-zA-Z_]+([-.]?[0-9a-zA-Z_]+)*@[0-9a-z]+\.[a-z]+$")
    return _check_valid(_email_valid, s = s)

# DREC-only groups
def is_valid_group(n):
    all_faculties = Faculty.objects.all()
    for f in all_faculties:
        if f.is_group_in_faculty(n):
            return True
    # depricated, for DREC-only MIPT groups
    _group_valid = re.compile(r"^[1-9]1[1-9][а-я]?$")
    return _check_valid(_group_valid, s = str(n))

# vk id
def is_valid_id_url(s):
    _id_valid_url = re.compile(r"^((https?://)?(m.)?vk.com/)?((((i|I)d)?[0-9]+)|([0-9a-zA-Z_\.]+))$")
    return _check_valid(_id_valid_url, s = s)

# С01-419
def is_valid_faculty(s):
    _faculty_valid = re.compile(r"^([0-9A-Za-zА-Яа-яЁё\-_])+(,([0-9A-Za-zА-Яа-яЁё\-_])+)+,?$")
    return _check_valid(_faculty_valid, s = s)

