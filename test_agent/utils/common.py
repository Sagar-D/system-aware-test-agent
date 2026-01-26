from uuid import UUID

def is_valid_uuid(value):
    try:
        UUID(str(value))
        return True
    except ValueError:
        return False

