class ValidatedString:

  def __set_name__(self, owner, name):
    self.public_name = name

  def __get__(self, obj, objtype=None):
    if obj is None:
      return self
    return obj.__dict__.get(self.public_name, "")

  def __set__(self, obj, value):
    if not isinstance(value, str):
      raise TypeError(f"'{self.public_name}' must be a string")
    if len(value) == 0:
      raise ValueError(f"'{self.public_name}' cannot be empty")
    obj.__dict__[self.public_name] = value


class UserProfile:
  username = ValidatedString()  # Using the descriptor

  def __init__(self, username):
    self.username = username


user = UserProfile("coder123")
print(user.username)
# user.username = ""  # Raises ValueError: 'username' cannot be empty