from store.audit_log import log_action
from store.postgres_store import (get_commits_for_single_feature,
                                  update_commit_status, update_test_status)
from store.qdrant_store import delete_vector


def manual_update(workspace_id, feature_id, item_type, item_id, text, author):
    collection = workspace_id
    if feature_id is not None:
        feature_id = feature_id.split(" - ")[1]
    print(f"Item_type: {item_type}", flush=True)
    if item_type == "Test":
        field = "test_name"
    elif item_type == "Commit":
        field = "commit_ID"
    try:
        delete_vector(collection, field, item_id)
        if item_type == "Test":
            commit_ID = get_commits_for_single_feature(
                workspace_id, feature_id, test_name=item_id
            )
            update_test_status(
                workspace_id,
                feature_id,
                commit_ID=commit_ID,
                test_name=item_id,
                status="Pending",
                delete=True,
            )
        elif item_type == "Commit":
            update_commit_status(
                workspace_id,
                feature_id,
                commit_ID=item_id,
                status="Pending",
                delete=True,
            )
        log_action(
            "Manual Override",
            f"Deleted {item_type} `{item_id}` from Feature `{feature_id}`",
            f"{text} - Author: {author}",
        )
        return f"✅ Deleted {item_type} `{item_id}` from Feature `{feature_id}`"
    except Exception as e:
        return f"❌ Error during delete: {str(e)}"
