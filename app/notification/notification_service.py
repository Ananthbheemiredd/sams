# app/notification/notification_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user_details import UserDetail
from app.models.notification import Notification
from app.notification.notifications import manager
from app.services.email import send_email


async def notify_user(
    *,
    db: AsyncSession,
    user_id: int,
    role: str,
    module: str,
    message: str,
    title: str,
    data: dict | None = None,
    email: str | None = None,
):
    """
    CENTRAL NOTIFICATION ENGINE FOR ENTIRE SAMS
    Used by: Applications, Fees, Academic, Admissions, Calendar, etc.
    """

    # -----------------------------------------------------
    # FK SAFETY CHECK (important)
    # -----------------------------------------------------
    result = await db.execute(
        select(UserDetail).where(UserDetail.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return

    # -----------------------------------------------------
    # SAVE IN-APP NOTIFICATION (DB)
    # -----------------------------------------------------
    notification = Notification(
        user_id=user_id,
        role=role,
        module=module,
        title=title,
        message=message,
        data=data,
        is_read=False,
    )

    db.add(notification)
    await db.commit()
    await db.refresh(notification)

    # -----------------------------------------------------
    # REAL TIME WEBSOCKET PUSH
    # -----------------------------------------------------
    await manager.send_to_user(
        user_id,
        {
            "id": notification.notification_id,
            "title": title,
            "message": message,
            "module": module,
            "data": data,
            "created_at": str(notification.created_at),
        }
    )

    # -----------------------------------------------------
    # EMAIL TO SYSTEM USER (UserDetail.email)
    # -----------------------------------------------------
    try:
        if user.email:
            ok = send_email(
                to_email=user.email,
                subject=title,
                text=f"{message}\n\n{data}",
            )
            notification.email_sent = ok
            notification.email_error = None if ok else "Email failed"
            await db.commit()
    except Exception as e:
        notification.email_error = str(e)
        await db.commit()

    # -----------------------------------------------------
    # EMAIL TO EXTERNAL EMAIL (like Application form)
    # -----------------------------------------------------
    try:
        if email:
            ok = send_email(
                to_email=email,
                subject=title,
                text=f"{message}\n\n{data}",
            )
            notification.email_sent = ok
            notification.email_error = None if ok else "Email failed"
            await db.commit()
    except Exception as e:
        notification.email_error = str(e)
        await db.commit()
