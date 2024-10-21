from django.contrib.auth.backends import BaseBackend

class SimpleBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        user_data_file = "user_data.txt"
        with open(user_data_file) as f:
            for line in f:
                uname, pword = line.strip().split(':')
                if username == uname and password == pword:
                    return self.get_user(username)
        return None

    def get_user(self, username):
        return SimpleUser(username=username)

class SimpleUser:
    is_authenticated = True
    is_staff = False
    is_superuser = False
    def __init__(self, username):
        self.username = username
        self.email = f"{username}@example.com"

    def get_username(self):
        return self.username

    def check_password(self, raw_password):
        user_data_file = "user_data.txt"
        with open(user_data_file) as f:
            for line in f:
                uname, pword = line.strip().split(':')
                if self.username == uname and raw_password == pword:
                    return True
        return False
