import argparse
import subprocess
import sys

import boto.s3.acl

from s3repo.repo import Repo

def Main(args=sys.argv[1:]):
  try:
    DEFAULT_CODENAME = subprocess.check_output(["lsb_release", "--codename",
      "--short"]).strip()
  except subprocess.CalledProcessError:
    DEFAULT_CODENAME = None

  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("-b", "--bucket",
    help="The name of the S3 bucket")
  parser.add_argument("-p", "--prefix", default="/",
    help="A string to be prepended to the S3 key names")
  parser.add_argument("--acl", default="authenticated-read",
    help="The default S3 ACL for created/modified keys.",
    choices=boto.s3.acl.CannedACLStrings)
  parser.add_argument("--component", default="main",
    help="The component where packages are placed. Only one is supported.")
  parser.add_argument("--codename",
    help="The codename of the target Debian/Ubuntu release",
    default=DEFAULT_CODENAME)
  parser.add_argument("--architectures", default="amd64 i386",
    help="A whitespace separated list of the supported architectures")

  sub_parsers = parser.add_subparsers()
  sub_parser = sub_parsers.add_parser("init")

  # `init` subcommand
  def InitMain(repo, options):
    repo.Init()
  sub_parser.set_defaults(function=InitMain)

  # `add` subcommand
  sub_parser = sub_parsers.add_parser("add")
  sub_parser.add_argument("--keep-old", action="store_true")
  sub_parser.add_argument("path", nargs="+")

  def AddMain(repo, options):
    for path in options.path:
      repo.AddPackage(path, remove_old_versions=not options.keep_old)
  sub_parser.set_defaults(function=AddMain)

  # `remove` subcommand
  sub_parser = sub_parsers.add_parser("remove")
  sub_parser.add_argument("package_name", nargs="+")

  def RemoveMain(repo, options):
    for package_name in options.package_name:
      repo.RemovePackage(package_name=package_name)
  sub_parser.set_defaults(function=RemoveMain)

  options = parser.parse_args(args)
  repo = Repo(bucket=options.bucket, prefix=options.prefix, acl=options.acl,
    component=options.component, codename=options.codename,
    architectures=options.architectures.split())

  options.function(repo, options)
