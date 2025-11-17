#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar roles y asignarlos a usuarios
"""

import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from src.db.models import Rol, Usuario

def setup_roles():
    """Crea los roles básicos del sistema"""
    db: Session = SessionLocal()
    
    try:
        # Verificar si existen roles
        roles_count = db.query(Rol).count()
        print(f"📊 Roles existentes: {roles_count}")
        
        # Crear rol Admin si no existe
        admin_role = db.query(Rol).filter(Rol.nombre == "Administrador").first()
        if not admin_role:
            admin_role = Rol(
                nombre="Administrador",
                descripcion="Acceso completo al sistema. Puede crear usuarios, gestionar datos y configurar el sistema."
            )
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print(f"✅ Rol 'Administrador' creado (ID: {admin_role.id_rol})")
        else:
            print(f"ℹ️  Rol 'Administrador' ya existe (ID: {admin_role.id_rol})")
        
        # Crear rol Usuario si no existe
        user_role = db.query(Rol).filter(Rol.nombre == "Usuario").first()
        if not user_role:
            user_role = Rol(
                nombre="Usuario",
                descripcion="Acceso estándar. Puede ver y gestionar datos de infantes y seguimientos."
            )
            db.add(user_role)
            db.commit()
            db.refresh(user_role)
            print(f"✅ Rol 'Usuario' creado (ID: {user_role.id_rol})")
        else:
            print(f"ℹ️  Rol 'Usuario' ya existe (ID: {user_role.id_rol})")
        
        print("\n" + "="*60)
        print("📋 ASIGNANDO ROLES A USUARIOS")
        print("="*60)
        
        # Asignar rol Admin a admin@example.com
        admin_user = db.query(Usuario).filter(Usuario.correo == "admin@example.com").first()
        if admin_user:
            if not admin_user.rol_id:
                admin_user.rol_id = admin_role.id_rol
                db.commit()
                print(f"✅ Rol 'Administrador' asignado a {admin_user.nombre} ({admin_user.correo})")
            else:
                print(f"ℹ️  {admin_user.nombre} ya tiene rol asignado (ID: {admin_user.rol_id})")
        else:
            print(f"⚠️  Usuario admin@example.com no encontrado")
        
        # Asignar rol Usuario a prueba@example.com
        test_user = db.query(Usuario).filter(Usuario.correo == "prueba@example.com").first()
        if test_user:
            if not test_user.rol_id:
                test_user.rol_id = user_role.id_rol
                db.commit()
                print(f"✅ Rol 'Usuario' asignado a {test_user.nombre} ({test_user.correo})")
            else:
                # Actualizar a usuario normal si tenía admin
                old_rol = test_user.rol_id
                test_user.rol_id = user_role.id_rol
                db.commit()
                print(f"✅ Rol de {test_user.nombre} actualizado de {old_rol} a {user_role.id_rol}")
        else:
            print(f"⚠️  Usuario prueba@example.com no encontrado")
        
        print("\n" + "="*60)
        print("📊 RESUMEN DE USUARIOS Y ROLES")
        print("="*60)
        
        usuarios = db.query(Usuario).all()
        for user in usuarios:
            rol_nombre = user.rol.nombre if user.rol else "Sin rol"
            print(f"👤 {user.nombre:30} | {user.correo:25} | Rol: {rol_nombre}")
        
        print("\n✅ Configuración de roles completada exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_roles()
