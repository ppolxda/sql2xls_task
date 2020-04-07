import re


RE_REGIX = re.compile(r'^([A-Za-z0-9\.\+_-]+)@([A-Za-z0-9\._-]+\.[a-zA-Z]*)$')


def encode_email(email):
    email_groups = re.match(RE_REGIX, email)
    if len(email) > 0 and email_groups is not None:
        mail = email_groups.group(1)
        size = len(mail)
        if size <= 2:
            return email
        elif size == 3:
            return mail[0] + '***' + mail[2] + '@' + email_groups.group(2)
        elif size == 4:
            return mail[0:1] + '***' + mail[2:4] + '@' + email_groups.group(2)
        elif size == 5:
            return mail[0:2] + '***' + mail[3:6] + '@' + email_groups.group(2)
        elif size == 6:
            return mail[0:2] + '***' + mail[4:7] + '@' + email_groups.group(2)
        elif size == 7:
            return mail[0:2] + '***' + mail[4:8] + '@' + email_groups.group(2)
        elif size == 8:
            return mail[0:2] + '***' + mail[5:10] + '@' + email_groups.group(2)
        elif size == 9:
            return mail[0:3] + '***' + mail[6:9] + '@' + email_groups.group(2)
        elif size == 10:
            return mail[0:3] + '***' + mail[7:10] + '@' + email_groups.group(2)
        elif size == 11:
            return mail[0:3] + '***' + mail[7:11] + '@' + email_groups.group(2)
        else:
            temp = mail[0:4]
            temp += '*' * max(len(mail) - 8, 5)
            return temp + mail[-4:] + '@' + email_groups.group(2)

        return email

    return None


def encode_string(string):
    if len(string) > 0:
        size = len(string)
        if size <= 2:
            return string
        elif size == 3:
            return string[0] + '***' + string[2]
        elif size == 4:
            return string[0:1] + '***' + string[2:4]
        elif size == 5:
            return string[0:2] + '***' + string[3:6]
        elif size == 6:
            return string[0:2] + '***' + string[4:7]
        elif size == 7:
            return string[0:2] + '***' + string[4:8]
        elif size == 8:
            return string[0:2] + '***' + string[5:10]
        elif size == 9:
            return string[0:3] + '***' + string[6:9]
        elif size == 10:
            return string[0:3] + '***' + string[7:10]
        elif size == 11:
            return string[0:3] + '***' + string[7:11]
        else:
            temp = string[0:4]
            temp += '*' * max(len(string) - 8, 5)
            return temp + string[-4:]

        return string

    return None


def string_line(val):
    return val
