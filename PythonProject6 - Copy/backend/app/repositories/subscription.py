from datetime import datetime, timedelta
import uuid

from backend.app.models.Member import Member
from backend.app.models.Plan import Plan
from backend.app.models.Subscription import Subscription
from backend.app.models.enums import SubscriptionStatus
from backend.app.exceptions.exceptions import NotFoundError, DuplicateError

class db_Subscription:
    def __init__(self, db_manager):
        self.SessionLocal = db_manager.SessionLocal

    def assign_subscription(self, member_id: str, plan_id: str, start_date=None):
        start_date = start_date or datetime.now()

        with self.SessionLocal() as session:
            try:
                member = session.query(Member).filter(Member.id == member_id).first()
                if member is None:
                    raise NotFoundError("Member not found")

                plan = session.query(Plan).filter(Plan.id == plan_id).first()
                if plan is None:
                    raise NotFoundError("Plan not found")

                active_sub = (
                    session.query(Subscription)
                    .filter(
                        Subscription.member_id == member_id,
                        Subscription.status == SubscriptionStatus.ACTIVE.value
                    )
                    .first()
                )
                if active_sub is not None:
                    raise DuplicateError("Active subscription already exists")

                end_date = start_date + timedelta(days=plan.valid_days)

                sub = Subscription(
                    id=uuid.uuid4().hex[:15],
                    member_id=member_id,
                    plan_id=plan_id,
                    status=SubscriptionStatus.ACTIVE.value,  # Enum value stored as string
                    start_date=start_date,
                    end_date=end_date,
                    remaining_entries=plan.max_entries,
                    frozen_until=None
                )

                session.add(sub)
                session.commit()
                return sub

            except Exception:
                session.rollback()
                raise

    def freeze_subscription(self, subscription_id: str, days: int):
        with self.SessionLocal() as session:
            try:
                sub = session.query(Subscription).filter(Subscription.id == subscription_id).first()
                if sub is None:
                    raise NotFoundError("Subscription not found")
                if sub.status != SubscriptionStatus.ACTIVE.value:
                    raise DuplicateError("Subscription is not active")

                now = datetime.now()

                if sub.frozen_until is None or sub.frozen_until <= now:
                    sub.frozen_until = now + timedelta(days=days)
                else:
                    sub.frozen_until = sub.frozen_until + timedelta(days=days)

                sub.status = SubscriptionStatus.FROZEN.value
                session.commit()
                return sub

            except Exception:
                session.rollback()
                raise

    def unfreeze_subscription(self, subscription_id: str):
        with self.SessionLocal() as session:
            try:
                sub = session.query(Subscription).filter(Subscription.id == subscription_id).first()
                if sub is None:
                    raise NotFoundError("Subscription not found")
                if sub.status != SubscriptionStatus.FROZEN.value:
                    raise DuplicateError("Subscription is not frozen")

                sub.frozen_until = None
                sub.status = SubscriptionStatus.ACTIVE.value
                session.commit()
                return sub

            except Exception:
                session.rollback()
                raise

    def get_subscription_status(self, subscription_id: str):
        with self.SessionLocal() as session:
            sub = session.query(Subscription).filter(Subscription.id == subscription_id).first()
            if sub is None:
                raise NotFoundError("Subscription not found")

            now = datetime.now()

            if sub.status == SubscriptionStatus.FROZEN.value:
                return SubscriptionStatus.FROZEN.value
            if now < sub.start_date or now > sub.end_date:
                return SubscriptionStatus.EXPIRED.value
            return SubscriptionStatus.ACTIVE.value
