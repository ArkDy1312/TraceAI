import hashlib

from sqlalchemy.orm import Session

from store.audit_log import ItemCache, engine


def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def is_changed(item_id: str, text: str) -> bool:
    h = compute_hash(text)
    session = Session(bind=engine)
    entry = session.get(ItemCache, item_id)
    if entry and entry.content_hash == h:
        session.close()
        return False
    session.close()
    return True


def update_cache(item_id: str, item_type: str, text: str):
    h = compute_hash(text)
    session = Session(bind=engine)
    entry = session.get(ItemCache, item_id)
    if entry:
        entry.content_hash = h
    else:
        entry = ItemCache(id=item_id, content_hash=h, item_type=item_type)
        session.add(entry)
    session.commit()
    session.close()
