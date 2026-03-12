from app.notification.notification_service import notify_user

async def emit_event(
    event: str,
    class_name: str,
    section: str,
    subject_or_title: str,
    actor_id: int,
    db
):
    await notify_user(
        event=event,
        class_name=class_name,
        section=section,
        subject=subject_or_title,
        actor_id=actor_id,
        db=db
    )




