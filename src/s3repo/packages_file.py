import gzip
import StringIO
from s3repo.field_set import FieldSet

from boto.s3.key import Key

def GzipCompress(str):
  out_stream = StringIO.StringIO()
  gzip.GzipFile("stdin", "w", 9, out_stream).write(str)
  return out_stream.getvalue()

class PackagesFile(object):
  def __init__(self, contents):
    self.packages = []
    for package_str in contents.split("\n\n"):
      if package_str == "":
        continue
      self.packages.append(FieldSet(package_str))

  @classmethod
  def Load(cls, bucket, bucket_path):
    return cls(Key(bucket=bucket, name=bucket_path).get_contents_as_string())

  def Store(self, bucket, bucket_path, acl):
    key = Key(bucket=bucket, name=bucket_path)
    self_str = str(self)
    key.set_contents_from_string(self_str, policy=acl)

    key = Key(bucket=bucket, name=bucket_path + ".gz")
    self_str_gz = GzipCompress(self_str)
    key.set_contents_from_string(self_str_gz, policy=acl)

    return self_str, self_str_gz

  def AddPackage(self, metadata):
    self.packages.append(metadata)

  def RemovePackage(self, name):
    for package in self.packages[:]:
      if package["Package"] == name:
        self.packages.remove(package)
        yield package["Filename"]

  def __str__(self):
    return "\n\n".join(map(str, self.packages))
