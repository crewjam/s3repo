
class FieldSet(object):
  def __init__(self, str):
    self.fields = []
    for line in str.strip().split("\n"):
      if not line:
        continue
      if line.startswith(" "):
        key, value = self.fields[-1]
        self.fields.pop(-1)

        value += "\n" + line.lstrip()
        self.fields.append((key, value))
      else:
        key, value = line.split(":", 1)
        self.fields.append((key, value.lstrip()))

  def __str__(self):
    rv = ""
    for (key, value) in self.fields:
      rv += key + ": " + value.replace("\n", "\n  ") + "\n"
    return rv

  def __getitem__(self, key):
    for (key_, value) in self.fields:
      if key_ == key:
        return value

  def __setitem__(self, key, value):
    for i, (key_, value_) in enumerate(self.fields):
      if key_ == key:
        self.fields[i] = (key, value)
        return
    self.fields.append((key, value))

  def __iter__(self):
    return iter(self.fields)
