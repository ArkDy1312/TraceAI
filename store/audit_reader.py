from sqlalchemy.orm import Session
from store.audit_log import AuditLog, engine
import pandas as pd


def get_audit_logs(limit=50):
    session = Session(bind=engine)
    logs = (
        session.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    )
    session.close()

    return pd.DataFrame(
        [
            {
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "agent": log.agent,
                "action": log.action,
                "details": log.details,
            }
            for log in logs
        ]
    )


def get_manual_overrides(limit=50):
    session = Session(bind=engine)
    logs = (
        session.query(AuditLog)
        .filter(AuditLog.agent == "Manual Override")
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
        .all()
    )
    session.close()

    return pd.DataFrame(
        [
            {
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "action": log.action,
                "details": log.details,
            }
            for log in logs
        ]
    )
