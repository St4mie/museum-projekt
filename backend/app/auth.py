# app/auth.py

import secrets
from enum import Enum
from typing import Dict, Tuple, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import settings

security = HTTPBasic()

# 1) Zentrale Rollen-Definition
class Role(str, Enum):
    EDITOR    = "editor"
    SERVICE   = "service"
    DEVELOPER = "developer"

# 2) Credentials-Mapping aus .env via Settings
#    Format: username → (password, role)
_CREDENTIALS: Dict[str, Tuple[str, Role]] = {
    settings.EDITOR_USER:  (settings.EDITOR_PASS,  Role.EDITOR),
    settings.SERVICE_USER: (settings.SERVICE_PASS, Role.SERVICE),
    settings.DEV_USER:     (settings.DEV_PASS,     Role.DEVELOPER),
}

def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security)
) -> Dict[str, str]:
    """
    Prüft User/Pass gegen die .env-Settings und gibt ein dict mit
    'username' und 'role' (Role-Enum) zurück.
    Liefert bei ungültigen Anmeldedaten eine 401 mit WWW-Authenticate-Header.
    """
    # Suche Eintrag
    entry = _CREDENTIALS.get(credentials.username)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Benutzer",
            headers={"WWW-Authenticate": 'Basic realm="museum-projekt"'},
        )

    correct_pass, role = entry
    if not secrets.compare_digest(credentials.password, correct_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falsches Passwort",
            headers={"WWW-Authenticate": 'Basic realm="museum-projekt"'},
        )

    return {"username": credentials.username, "role": role.value}

def require_role(allowed_roles: List[Role]):
    """
    Factory für rollenbasierte Zugriffskontrolle.
    Hebt bei fehlender Rolle eine 403 (ohne WWW-Authenticate) aus.
    """
    def role_checker(user = Depends(get_current_user)):
        user_role = Role(user["role"])
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Keine ausreichende Berechtigung",
            )
        return user
    return role_checker
