import boto3

def get_session(account_details):
    
    session = boto3.Session(
        aws_access_key_id=account_details["aws_access_key_id"],
        aws_secret_access_key=account_details["aws_secret_access_key"],
        region_name=account_details["region_name"]
    )
    return session