class FakeUser:
    def __init__(self):
        self.id = 1
        self.email = "test@example.com"


def get_current_user():
    return FakeUser()


def get_current_user_optional():
    return None
