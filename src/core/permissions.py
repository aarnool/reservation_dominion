ROLES_SCOOPES = {
    "admin": [
        "resources:create", 
        "resources:read", 
        "resources:update", 
        "resources:delete", 
        "reservations:create", 
        "reservations:read", 
        "reservations:update", 
        "reservations:delete",
        "reservations:approve"
    ],
    
    "user": [
        "resources:read", 
        "reservations:create", 
        "reservations:read", 
        "reservations:update", 
        "reservations:delete"],
}