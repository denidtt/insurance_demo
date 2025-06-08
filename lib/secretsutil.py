import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

session = boto3.session.Session()


def get_secret(secret_name, region_name):
    """
    Get Secret for a secret Name will be parameterised later

    :return:  secret string
    """

    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except NoCredentialsError:
        print("AWS credentials not found. Please configure them.")
    except PartialCredentialsError:
        print("Incomplete AWS credentials. Please check your configuration.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return get_secret_value_response['SecretString']
