"""Ensure an admin role and user exist in the configured database.

Usage:
  DATABASE_URL="sqlite:///./test.db" python ensure_admin.py

This script uses the project's SQLAlchemy session and models so it will
operate against the same DB the app uses.
"""
import os
import sys
from pathlib import Path

# Ensure project `src` package is on sys.path so imports like `core` resolve
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.db.session import SessionLocal
from src.db.models import Rol, Usuario
from core.security import get_password_hash


def ensure_admin():
    db = SessionLocal()
    try:
        admin_role = db.query(Rol).filter(Rol.nombre.ilike("administrador")).first()
        if not admin_role:
            admin_role = Rol(nombre="Administrador", descripcion="Rol administrador creado por ensure_admin.py")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print(f"Created role Administrador (id={admin_role.id_rol})")
        else:
            print(f"Found role Administrador (id={admin_role.id_rol})")

        # Look for any user assigned to admin_role
        admin_user = db.query(Usuario).filter(Usuario.rol_id == admin_role.id_rol).first()
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_phone = os.getenv("ADMIN_PHONE", "3000000000")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

        if not admin_user:
            # If no user with the role exists, check by email
            existing = db.query(Usuario).filter(Usuario.correo == admin_email).first()
            if existing:
                existing.rol_id = admin_role.id_rol
                existing.contrasena = get_password_hash(admin_password)
                db.commit()
                print(f"Assigned existing user {admin_email} to Administrador and updated password")
            else:
                nuevo = Usuario(
                    nombre="Administrador",
                    correo=admin_email,
                    telefono=admin_phone,
                    contrasena=get_password_hash(admin_password),
                    rol_id=admin_role.id_rol,
                )
                db.add(nuevo)
                db.commit()
                db.refresh(nuevo)
                print(f"Created admin user {admin_email}")
        else:
            print(f"Found admin user with role Administrador: {admin_user.correo}")
            # If the password looks like a placeholder, update it
            if isinstance(admin_user.contrasena, str) and admin_user.contrasena.startswith("hashed_password"):
                admin_user.contrasena = get_password_hash(admin_password)
                db.commit()
                print("Replaced placeholder admin password with hashed ADMIN_PASSWORD")

    finally:
        db.close()


if __name__ == "__main__":
    ensure_admin()
