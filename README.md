This is a tool to manage simple Debian repositories in Amazon S3. 

Example:

    $ cat ~/.boto
    [Credentials]
    aws_access_key_id = XXXXXXXXXXXXXXXXXXXX
    aws_secret_access_key = YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY

    $ s3repo --bucket=mybucket --codename=precise --prefix=private/mystuff init
  
    $ s3repo --bucket=mybucket --codename=precise --prefix=private/mystuff add ~/myapp.deb

By default add removes old versions unless you specify --keep-old

In /etc/apt/sources.list or whatever:

    deb s3://XXXXXXXXXXXXXXXXXXXX:YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY@s3.amazonaws.com/mybucket/private/mystuff precise main

The s3:// transport for APT is from apt-s3 (https://github.com/kyleshank/apt-s3)
