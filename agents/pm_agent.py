from store.audit_log import log_action
from utils.delta_checker import is_changed, update_cache
from store.postgres_store import insert_feature
from state.trace_state import TraceState

def pm_agent_step(state: TraceState) -> TraceState:
    updated_features = []

    for raw_feature in state.get("feature_specs", []):
        clean_text = raw_feature["description"]

        if not is_changed(raw_feature["feature_id"], clean_text):
            log_action("PM Agent", "Skipped unchanged feature", raw_feature["feature_id"])
            continue

        metadata = {
            "feature_id": raw_feature["feature_id"],
            "title": raw_feature["title"],
            "description": clean_text,
            "author": raw_feature["author"]
        }

        # Store in PostgreSQL instead of Qdrant
        insert_feature(
            workspace_id=state["workspace_id"],
            feature_id=metadata["feature_id"],
            title=metadata["title"],
            description=clean_text,
            author=raw_feature["author"]
        )

        update_cache(raw_feature["feature_id"], "feature", clean_text)
        log_action("PM Agent", "Stored new feature", str(metadata))

        updated_features.append(raw_feature)

    if not updated_features:
        return state

    return {
        **state,
        "feature_specs": updated_features
    }
