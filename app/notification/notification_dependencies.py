from sqlalchemy.orm import Session
from app.models.notification import Notification


def create_notification(
    db: Session,
    title: str,
    message: str,
    module: str,
    reference_id: int | None = None,
    user_id: str | None = None
):
    notification = Notification(
        title=title,
        message=message,
        module=module,
        reference_id=reference_id,
        user_id=user_id
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification
