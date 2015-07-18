import re

def valid_uuid(uuid):
    '''
    validate that the 'uuid' is a uuid4
    '''
    regex = re.compile((
        '^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}'
        '-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z'
    ), re.I)
    match = regex.match(str(uuid))

    if match:
        return uuid
    return False
