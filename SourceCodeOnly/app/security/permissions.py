import enum

class Permission(str, enum.Enum):
    READ_DOCUMENT = "read:document"
    WRITE_DOCUMENT = "write:document"
    DELETE_DOCUMENT = "delete:document"
    
    READ_ASSET = "read:asset"
    
    READ_ANALYTICS = "read:analytics"
    
    MANAGE_USERS = "manage:users"
    
    # Catch-all
    ADMIN = "admin:all"
