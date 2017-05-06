import hashlib
import string
import random

SECRET = 'qwertyasdfgzxcvb'


def get_salt():
    salt = ''
    for i in range(0, 5):
        salt = salt + random.choice(string.ascii_letters)
    return salt


def get_hash(value):
    return hashlib.sha256(value).hexdigest()


def hash_password(password, salt=''):
    if not salt:
        salt = get_salt()
    return "{}|".format(salt) + get_hash(password + salt)


def make_secure_cookie(self, value):
    return "{}|{}".format(value, hashlib.sha256(self.SECRET + str(value)).hexdigest())


def validate_cookie(cookie):
    x = cookie.split('|')[0]
    if cookie == make_secure_cookie(x):
        return x


def validate_password(password, pw_hash):
    salt = pw_hash.split('|')[0]
    if pw_hash == hash_password(password, salt):
        return pw_hash
