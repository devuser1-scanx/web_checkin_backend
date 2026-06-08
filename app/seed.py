from app.database import SessionLocal
from app.models.role import RoleWebCheckin
from app.models.user import UserWebCheckin
from app.utils.security import hash_password


def seed():
    db = SessionLocal()

    try:
        admin_role = db.query(RoleWebCheckin).filter(
            RoleWebCheckin.role_name == "admin"
        ).first()

        if not admin_role:
            admin_role = RoleWebCheckin(
                role_name="admin",
                description="Full administrative access",
                is_system_role=True,
            )
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)

        staff_role = db.query(RoleWebCheckin).filter(
            RoleWebCheckin.role_name == "staff"
        ).first()

        if not staff_role:
            staff_role = RoleWebCheckin(
                role_name="staff",
                description="Can only check in and check out",
                is_system_role=True,
            )
            db.add(staff_role)
            db.commit()

        admin_user = db.query(UserWebCheckin).filter(
            UserWebCheckin.username == "admin"
        ).first()

        if not admin_user:
            admin_user = UserWebCheckin(
                full_name="ScanX Admin",
                username="admin",
                email="admin@scanx.local",
                password_hash=hash_password("Admin@123"),
                role_id=admin_role.id,
                status="active",
                is_active=True,
                is_deleted=False,
            )
            db.add(admin_user)
            db.commit()

            print("Admin user created.")
            print("Username: admin")
            print("Password: Admin@123")
        else:
            print("Admin user already exists.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()