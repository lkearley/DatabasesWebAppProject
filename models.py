from werkzeug.security import check_password_hash
import enum
import hashlib


class Type(enum.Enum):
    ADMIN = "Admin"
    OWNER = "Owner"
    VISITOR = "Visitor"


class User:
    def __init__(self, username, email, password, usertype):
        self.username = username
        self.email = email
        self.set_password(password)
        self.usertype = usertype
        #self.password_hash = None

    def set_password(self, password):
        self.password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
