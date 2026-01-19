"""
Seed/Dummy Data Script for FitTrack Gym Management System

This script creates all required database tables and inserts realistic demo data.
Supports rerun without crashing (drops tables first if they exist).

Usage:
    python seed.py
"""
import os
import sys
from datetime import datetime, timedelta
import uuid

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app.repositories.db_manager import SQLManger
from backend.app.models import (
    Base, Member, Trainer, Admin, Plan, Subscription, Payment, 
    ClassSession, Enrollment, Checkin, WorkoutPlan, WorkoutItem,
    WaitingList, ProgressLog
)
from backend.app.models.enums import (
    SubscriptionStatus, SessionStatus, EnrollmentStatus, 
    PaymentStatus, CheckinResult, PlanType, WaitingListStatus
)
from sqlalchemy import text


def generate_id():
    """Generate a 15-character ID."""
    return uuid.uuid4().hex[:15]


def seed_database(config_path="config.ini"):
    """
    Seed the database with dummy data.
    
    Args:
        config_path: Path to database configuration file
    """
    print("🌱 Starting database seeding...")
    
    # Initialize database manager
    db_manager = SQLManger(config_path=config_path)
    
    # Test connection
    if not db_manager.test_connection():
        print("❌ Database connection failed!")
        return False
    
    print("✅ Database connection successful")
    
    # Drop all tables (for clean rerun)
    print("🗑️  Dropping existing tables...")
    try:
        with db_manager.engine.connect() as conn:
            # Disable foreign key checks temporarily
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            # Drop tables in reverse dependency order
            tables = [
                "progress_logs", "waiting_list", "workout_items", "workout_plans", 
                "checkin", "enrollment", "class_session", "payments", 
                "subscriptions", "plans", "admins", "trainers", "members"
            ]
            for table in tables:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS `{table}`"))
                    print(f"   Dropped table: {table}")
                except Exception as e:
                    print(f"   Warning: Could not drop {table}: {e}")
            
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            conn.commit()
    except Exception as e:
        print(f"   Warning: Error dropping tables: {e}")
        print("   Continuing anyway...")
    except Exception as e:
        print(f"   Warning: Error dropping tables: {e}")
        print("   Continuing anyway...")
    
    # Create all tables
    print("📋 Creating database tables...")
    Base.metadata.create_all(db_manager.engine)
    print("✅ Tables created successfully")
    
    # Start seeding data
    print("📦 Inserting dummy data...")
    session = db_manager.SessionLocal()
    
    try:
        # 1. Create Members
        print("   Creating members...")
        members = [
            Member(id="123456789", fullname="John Doe", email="john@example.com", phone="0501234567"),
            Member(id="987654321", fullname="Jane Smith", email="jane@example.com", phone="0529876543"),
            Member(id="111222333", fullname="Bob Johnson", email="bob@example.com", phone="0541112222"),
            Member(id="444555666", fullname="Alice Brown", email="alice@example.com", phone="0504445555"),
            Member(id="777888999", fullname="Charlie Wilson", email="charlie@example.com", phone="0527778888"),
        ]
        for member in members:
            session.add(member)
        session.commit()
        print(f"   ✅ Created {len(members)} members")
        
        # 2. Create Trainers (IDs must be 9 chars max)
        print("   Creating trainers...")
        trainers = [
            Trainer(id="TR001", fullname="Mike Trainer", email="mike@gym.com", phone="0501111111"),
            Trainer(id="TR002", fullname="Sarah Coach", email="sarah@gym.com", phone="0502222222"),
            Trainer(id="TR003", fullname="Tom Fitness", email="tom@gym.com", phone="0503333333"),
        ]
        for trainer in trainers:
            session.add(trainer)
        session.commit()
        print(f"   ✅ Created {len(trainers)} trainers")
        
        # 2.5. Create Admins
        print("   Creating admins...")
        admins = [
            Admin(id="ADMIN001", fullname="Admin Manager", email="admin@gym.com", phone="0500000000"),
            Admin(id="ADMIN002", fullname="System Admin", email="sysadmin@gym.com", phone="0500000001"),
        ]
        for admin in admins:
            session.add(admin)
        session.commit()
        print(f"   ✅ Created {len(admins)} admins")
        
        # 3. Create Plans
        print("   Creating subscription plans...")
        plans = [
            Plan(id="PLAN001", name="Basic Monthly", plan_type=PlanType.MONTHLY.value, price=199.99, valid_days=30, max_entries=20),
            Plan(id="PLAN002", name="Premium Monthly", plan_type=PlanType.MONTHLY.value, price=299.99, valid_days=30, max_entries=999),
            Plan(id="PLAN003", name="Basic Yearly", plan_type=PlanType.YEARLY.value, price=1999.99, valid_days=365, max_entries=240),
            Plan(id="PLAN004", name="Premium Yearly", plan_type=PlanType.YEARLY.value, price=2999.99, valid_days=365, max_entries=999),
            Plan(id="PLAN005", name="VIP Monthly", plan_type=PlanType.VIP.value, price=499.99, valid_days=30, max_entries=999),
        ]
        for plan in plans:
            session.add(plan)
        session.commit()
        print(f"   ✅ Created {len(plans)} plans")
        
        # 4. Create Subscriptions
        print("   Creating subscriptions...")
        now = datetime.now()
        subscriptions = [
            Subscription(
                id=generate_id(),
                member_id="123456789",
                plan_id="PLAN001",
                status=SubscriptionStatus.ACTIVE.value,
                outstanding_debt=0,
                start_date=now - timedelta(days=10),
                end_date=now + timedelta(days=20),
                remaining_entries=15,
                frozen_until=None
            ),
            Subscription(
                id=generate_id(),
                member_id="987654321",
                plan_id="PLAN002",
                status=SubscriptionStatus.ACTIVE.value,
                outstanding_debt=0,
                start_date=now - timedelta(days=5),
                end_date=now + timedelta(days=25),
                remaining_entries=999,
                frozen_until=None
            ),
            Subscription(
                id=generate_id(),
                member_id="111222333",
                plan_id="PLAN001",
                status=SubscriptionStatus.FROZEN.value,
                outstanding_debt=0,
                start_date=now - timedelta(days=20),
                end_date=now + timedelta(days=10),
                remaining_entries=5,
                frozen_until=now + timedelta(days=7)
            ),
        ]
        for sub in subscriptions:
            session.add(sub)
        session.commit()
        print(f"   ✅ Created {len(subscriptions)} subscriptions")
        
        # 5. Create Payments
        print("   Creating payments...")
        payments = [
            Payment(
                id=generate_id(),
                subscription_id=subscriptions[0].id,
                amount=199.99,
                status=PaymentStatus.PAID.value,
                paid_at=now - timedelta(days=10),
                reference="PAY001"
            ),
            Payment(
                id=generate_id(),
                subscription_id=subscriptions[1].id,
                amount=299.99,
                status=PaymentStatus.PAID.value,
                paid_at=now - timedelta(days=5),
                reference="PAY002"
            ),
        ]
        for payment in payments:
            session.add(payment)
        session.commit()
        print(f"   ✅ Created {len(payments)} payments")
        
        # 6. Create Class Sessions
        print("   Creating class sessions...")
        sessions = [
            ClassSession(
                id=generate_id(),
                title="Morning Yoga",
                starts_at=now + timedelta(days=1, hours=8),
                capacity=20,
                trainer_id="TR001",
                status=SessionStatus.OPEN.value
            ),
            ClassSession(
                id=generate_id(),
                title="Evening Cardio",
                starts_at=now + timedelta(days=2, hours=18),
                capacity=15,
                trainer_id="TR002",
                status=SessionStatus.OPEN.value
            ),
            ClassSession(
                id=generate_id(),
                title="Strength Training",
                starts_at=now + timedelta(days=3, hours=10),
                capacity=10,
                trainer_id="TR003",
                status=SessionStatus.OPEN.value
            ),
        ]
        for sess in sessions:
            session.add(sess)
        session.commit()
        print(f"   ✅ Created {len(sessions)} class sessions")
        
        # 7. Create Enrollments
        print("   Creating enrollments...")
        enrollments = [
            Enrollment(
                id=generate_id(),
                class_session_id=sessions[0].id,
                member_id="123456789",
                status=EnrollmentStatus.REGISTERED.value,
                created_at=now - timedelta(days=2),
                canceled_at=None,
                cancel_reason=None
            ),
            Enrollment(
                id=generate_id(),
                class_session_id=sessions[0].id,
                member_id="987654321",
                status=EnrollmentStatus.REGISTERED.value,
                created_at=now - timedelta(days=1),
                canceled_at=None,
                cancel_reason=None
            ),
            Enrollment(
                id=generate_id(),
                class_session_id=sessions[1].id,
                member_id="111222333",
                status=EnrollmentStatus.REGISTERED.value,
                created_at=now - timedelta(days=3),
                canceled_at=None,
                cancel_reason=None
            ),
        ]
        for enroll in enrollments:
            session.add(enroll)
        session.commit()
        print(f"   ✅ Created {len(enrollments)} enrollments")
        
        # 8. Create Check-ins
        print("   Creating check-ins...")
        checkins = [
            Checkin(
                id=generate_id(),
                member_id="123456789",
                created_at=now - timedelta(days=1, hours=10),
                result=CheckinResult.APPROVED.value,
                reason=None
            ),
            Checkin(
                id=generate_id(),
                member_id="987654321",
                created_at=now - timedelta(days=2, hours=14),
                result=CheckinResult.APPROVED.value,
                reason=None
            ),
            Checkin(
                id=generate_id(),
                member_id="123456789",
                created_at=now - timedelta(hours=8),
                result=CheckinResult.APPROVED.value,
                reason=None
            ),
        ]
        for checkin in checkins:
            session.add(checkin)
        session.commit()
        print(f"   ✅ Created {len(checkins)} check-ins")
        
        # 9. Create Workout Plans
        print("   Creating workout plans...")
        workout_plan = WorkoutPlan(
            id=generate_id(),
            member_id="123456789",
            trainer_id="TR001",
            title="Beginner Strength Program",
            created_at=now - timedelta(days=5),
            is_active=True
        )
        session.add(workout_plan)
        session.flush()  # Flush to get the ID
        
        # 10. Create Workout Items
        print("   Creating workout items...")
        workout_items = [
            WorkoutItem(
                id=generate_id(),
                workout_plan_id=workout_plan.id,
                exercise_name="Push Ups",
                sets=3,
                reps=12,
                target_weight=None,
                notes="Focus on form"
            ),
            WorkoutItem(
                id=generate_id(),
                workout_plan_id=workout_plan.id,
                exercise_name="Squats",
                sets=3,
                reps=15,
                target_weight=None,
                notes="Body weight only"
            ),
            WorkoutItem(
                id=generate_id(),
                workout_plan_id=workout_plan.id,
                exercise_name="Bench Press",
                sets=4,
                reps=8,
                target_weight=60.0,
                notes="Start with 60kg"
            ),
        ]
        for item in workout_items:
            session.add(item)
        session.commit()
        print(f"   ✅ Created {len(workout_items)} workout items")
        
        # 11. Create Waiting List Entries (for demonstration)
        print("   Creating waiting list entries...")
        # Add a member to waiting list for a full session
        full_session = sessions[2]  # Strength Training with capacity 10
        # Fill it up first with existing members
        existing_member_ids = ["123456789", "987654321", "111222333", "444555666", "777888999"]
        for i in range(min(10, len(existing_member_ids))):
            enroll = Enrollment(
                id=generate_id(),
                class_session_id=full_session.id,
                member_id=existing_member_ids[i],
                status=EnrollmentStatus.REGISTERED.value,
                created_at=now - timedelta(days=1),
                canceled_at=None,
                cancel_reason=None
            )
            session.add(enroll)
        session.flush()
        
        # Now add another member to waiting list (if we have more members)
        if len(existing_member_ids) > 5:
            # Use a member that's not already enrolled
            waiting_member_id = "777888999"  # Charlie Wilson
            waiting_entry = WaitingList(
                id=generate_id(),
                class_session_id=full_session.id,
                member_id=waiting_member_id,
                status=WaitingListStatus.WAITING.value,
                position=1,
                priority_score=100,
                created_at=now - timedelta(hours=2),
                assigned_at=None,
                confirmed_at=None,
                cancelled_at=None,
                approval_deadline=None
            )
            session.add(waiting_entry)
            session.commit()
            print(f"   ✅ Created 1 waiting list entry")
        else:
            session.commit()
            print(f"   ✅ Session filled (no waiting list needed)")
        
        # 12. Create Progress Logs
        print("   Creating progress logs...")
        progress_logs = [
            ProgressLog(
                id=generate_id(),
                workout_plan_id=workout_plan.id,
                workout_item_id=workout_items[0].id,
                member_id="123456789",
                exercise_name="Push Ups",
                sets_completed=3,
                reps_completed=12,
                weight_used=None,
                target_weight=None,
                duration_minutes=15,
                notes="Completed all sets",
                logged_at=now - timedelta(days=3)
            ),
            ProgressLog(
                id=generate_id(),
                workout_plan_id=workout_plan.id,
                workout_item_id=workout_items[2].id,
                member_id="123456789",
                exercise_name="Bench Press",
                sets_completed=4,
                reps_completed=8,
                weight_used=60.0,
                target_weight=60.0,
                duration_minutes=20,
                notes="Good form, increased weight next time",
                logged_at=now - timedelta(days=1)
            ),
        ]
        for log in progress_logs:
            session.add(log)
        session.commit()
        print(f"   ✅ Created {len(progress_logs)} progress logs")
        
        print("\n✅ Database seeding completed successfully!")
        print("\n📊 Summary:")
        print(f"   - Members: {len(members)}")
        print(f"   - Trainers: {len(trainers)}")
        print(f"   - Plans: {len(plans)}")
        print(f"   - Subscriptions: {len(subscriptions)}")
        print(f"   - Payments: {len(payments)}")
        print(f"   - Class Sessions: {len(sessions)}")
        print(f"   - Enrollments: {len(enrollments)}")
        print(f"   - Check-ins: {len(checkins)}")
        print(f"   - Workout Plans: 1")
        print(f"   - Workout Items: {len(workout_items)}")
        print(f"   - Waiting List Entries: 1")
        print(f"   - Progress Logs: {len(progress_logs)}")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(BASE_DIR, "config.ini")
    
    success = seed_database(config_path)
    sys.exit(0 if success else 1)
