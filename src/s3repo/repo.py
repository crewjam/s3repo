import hashlib
import os
import subprocess
from os.path import basename

import boto
from boto.s3.key import Key

from s3repo.field_set import FieldSet
from s3repo.release_file import ReleaseFile
from s3repo.packages_file import PackagesFile

class Repo(object):
  def __init__(self, bucket, prefix, acl, component, codename, architectures):
    self.bucket = boto.connect_s3().get_bucket(bucket)
    self.prefix = prefix.rstrip("/") + "/"
    self.acl = acl
    self.component = component
    self.codename = codename
    self.architectures = architectures

  def RemovePackage(self, package_name):
    files_to_delete = []
    for architecture in self.architectures:
      packages_file_relative_path = "dists/" + self.codename + "/" + \
        self.component + "/" + "binary-" + architecture + \
        "/Packages"
      packages = PackagesFile.Load(self.bucket,
        self.prefix + packages_file_relative_path)

      files_to_delete.extend(packages.RemovePackage(package_name))

      packages_str, packages_gz_str = packages.Store(self.bucket,
        self.prefix + packages_file_relative_path, acl=self.acl)

      release = ReleaseFile.Load(self.bucket, self.prefix + "dists/" +
        self.codename + "/Release")
      release.UpdateFile(self.component + "/" + "binary-" + architecture + \
        "/Packages", packages_str)
      release.UpdateFile(self.component + "/" + "binary-" + architecture + \
        "/Packages.gz", packages_gz_str)
      release.Store(self.bucket, self.prefix + "dists/" + self.codename +
        "/Release", acl=self.acl)

    for file_to_delete in files_to_delete:
      self.bucket.delete_key(self.prefix + file_to_delete)

  def AddPackage(self, path, remove_old_versions=False):
    metadata = FieldSet(subprocess.check_output(["dpkg-deb", "-I", path,
      "control"]))

    package = metadata["Package"]
    relative_path = "pool/" + self.component + "/" + package[0] + "/" + \
      package + "/" + basename(path)
    key = Key(bucket=self.bucket, name=self.prefix + relative_path)
    key.set_contents_from_filename(path, policy=self.acl)

    metadata["Filename"] = relative_path
    metadata["Size"] = str(os.stat(path).st_size)
    metadata["MD5"] = hashlib.md5(file(path, "rb").read()).hexdigest()
    metadata["SHA1"] = hashlib.sha1(file(path, "rb").read()).hexdigest()
    metadata["SHA256"] = hashlib.sha256(file(path, "rb").read()).hexdigest()

    if metadata["Architecture"] == "all":
      architectures = self.architectures[:]
    else:
      architectures = metadata["Architecture"].split()

    files_to_delete = []

    for architecture in architectures:
      packages_file_relative_path = "dists/" + self.codename + "/" + \
        self.component + "/" + "binary-" + architecture + \
        "/Packages"
      packages = PackagesFile.Load(self.bucket,
        self.prefix + packages_file_relative_path)

      if remove_old_versions:
        files_to_delete.extend(packages.RemovePackage(package))

      packages.AddPackage(metadata)

      packages_str, packages_gz_str = packages.Store(self.bucket,
        self.prefix + packages_file_relative_path, acl=self.acl)

      release = ReleaseFile.Load(self.bucket, self.prefix + "dists/" +
        self.codename + "/Release")
      release.UpdateFile(self.component + "/" + "binary-" + architecture + \
        "/Packages", packages_str)
      release.UpdateFile(self.component + "/" + "binary-" + architecture + \
        "/Packages.gz", packages_gz_str)
      release.Store(self.bucket, self.prefix + "dists/" + self.codename +
        "/Release", acl=self.acl)

    for file_to_delete in files_to_delete:
      self.bucket.delete_key(self.prefix + file_to_delete)

  def Init(self):
    distributions = FieldSet("")
    distributions["Codename"] = self.codename
    distributions["Components"] = self.component
    distributions["Architectures"] = " ".join(self.architectures)
    for line in subprocess.check_output(["gpg", "--list-secret-keys",
        "--with-colons"]).splitlines():
      parts = line.split(":")
      distributions["SignWith"] = parts[4][-8:]
    Key(bucket=self.bucket, name=self.prefix + "conf/distributions")\
      .set_contents_from_string(str(distributions), policy=self.acl)

    release = ReleaseFile.New(self.codename, self.architectures,
      self.component)

    for architecture in self.architectures:
      # Add empty package lists for each architecture
      packages_file_relative_path = "dists/" + self.codename + "/" + \
        self.component + "/" + "binary-" + architecture + \
        "/Packages"
      Key(bucket=self.bucket, name=self.prefix + packages_file_relative_path)\
        .set_contents_from_string("", policy=self.acl)
      release.UpdateFile(self.component + "/" + "binary-" + architecture + \
        "/Packages", "")
    release.Store(self.bucket, self.prefix + "dists/" + self.codename +
      "/Release", acl=self.acl)
