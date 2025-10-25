class User:
    def __init__(self, _id: str, name: str, phone: str, email: str, user_type: str):
        self._id = _id
        self.name = name
        self.phone = phone
        self.email = email
        self.type = user_type

    def __repr__(self):
        return f"User(name={self.name!r}, email={self.email!r}, type={self.type!r})"