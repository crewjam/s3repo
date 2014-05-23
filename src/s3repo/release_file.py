import email.utils
import hashlib
import subprocess

from boto.s3.key import Key
from s3repo.field_set import FieldSet


class ReleaseFile(object):
  def __init__(self, str):
    self.field_set = FieldSet(str)

  def UpdateFile(self, relative_path, contents):
    size = str(len(contents))
    self.field_set["Date"] = email.utils.formatdate()

    def ReplaceDigestLine(field_name, size, digest):
      updated = False
      new_lines = []
      for line in self.field_set[field_name].strip().splitlines():
        digest_, size_, path_ = line.strip().split(" ")
        if path_ == relative_path:
          digest_ = digest
          size_ = size
          updated = True
        new_lines.append(digest_ + " " + size_ + " " + path_)
      if not updated:
        new_lines.append(digest + " " + size + " " + relative_path)
      self.field_set[field_name] = "\n" + "\n".join(new_lines)

    ReplaceDigestLine("MD5Sum", size, hashlib.md5(contents).hexdigest())
    ReplaceDigestLine("SHA1", size, hashlib.sha1(contents).hexdigest())
    ReplaceDigestLine("SHA256", size, hashlib.sha256(contents).hexdigest())

  def __str__(self):
    return str(self.field_set)

  def Store(self, bucket, bucket_path, acl):
    release_key = Key(bucket=bucket, name=bucket_path)
    release_str = str(self)
    release_key.set_contents_from_string(release_str, policy=acl)

    release_gpg_str, _ = subprocess.Popen(["gpg", "--detach-sign", "--armor"],
      stdout=subprocess.PIPE, stdin=subprocess.PIPE).communicate(release_str)
    release_gpg_key = Key(bucket=bucket, name=bucket_path + ".gpg")
    release_gpg_key.set_contents_from_string(release_gpg_str, policy=acl)

  @classmethod
  def Load(cls, bucket, bucket_path):
    return cls(Key(bucket=bucket, name=bucket_path).get_contents_as_string())

  @classmethod
  def New(cls, dist, architectures, component):
    self = cls("")
    self.field_set["Codename"] = dist
    self.field_set["Architectures"] = " ".join(architectures)
    self.field_set["Components"] = component
    self.field_set["Date"] = email.utils.formatdate()
    self.field_set["MD5Sum"] = ""
    self.field_set["SHA1"] = ""
    self.field_set["SHA256"] = ""
    return self
