import re


def valid_uuid(uuid):
    '''
    validate that the 'uuid' is a uuid4
    '''
    if uuid in ('00000000-0000-0000-0000-000000000000',
                '11111111-1111-1111-1111-111111111111'):
        return uuid
    regex = re.compile((
        '^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}'
        '-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z'
    ), re.I)
    match = regex.match(str(uuid))

    if match:
        return uuid
    return False
