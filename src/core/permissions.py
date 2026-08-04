ROLES_SCOOPES = {
    "admin": [
        # Permisos de Recursos 
        "resources:create", 
        "resources:read", 
        "resources:update", 
        "resources:delete", 
        # Permisos de Reservaciones
        "reservations:create", 
        "reservations:read", 
        "reservations:update", 
        "reservations:delete",
        "reservations:approve",
        "reservations:read_all"
    ],
    
    "user": [
        # Permisos de Recursos
        "resources:read", 
        # Permisos de Reservaciones
        "reservations:create", 
        "reservations:read", 
        "reservations:update", 
        "reservations:delete",
        "reservations:cancel"
    ]
}