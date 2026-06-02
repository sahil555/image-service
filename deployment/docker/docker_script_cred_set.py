import boto3
import os
# Initialize a default session
session = boto3.Session()

# Fetch credential object
credentials = session.get_credentials()

if credentials is None:
    print("No AWS credentials available in the current environment. Skipping credential export.")
else:
    # Freeze credentials to resolve any deferred/temporary credentials
    read_creds = credentials.get_frozen_credentials()

    print("Access Key ID:", read_creds.access_key)
    print("Secret Access Key:", read_creds.secret_key)

    # export these as environment variables for the application to use
    if read_creds.access_key:
        os.environ["AWS_ACCESS_KEY_ID"] = read_creds.access_key
    if read_creds.secret_key:
        os.environ["AWS_SECRET_ACCESS_KEY"] = read_creds.secret_key

    os.execv("/bin/zsh", ["export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} && export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}"])