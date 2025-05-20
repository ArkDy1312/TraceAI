from state.trace_state import TraceState
from store.audit_log import log_action
from store.embedder import get_embedding
from store.postgres_store import feature_status, update_commit_status
from store.qdrant_store import init_collection, store_vector
from utils.delta_checker import is_changed, update_cache


def dev_agent_step(state: TraceState) -> TraceState:
    workspace_id = state["workspace_id"]
    collection = workspace_id
    init_collection(collection)

    updated_commits = []

    for raw_commit in state.get("code_links", []):
        feature_id = raw_commit["feature_id"]
        clean_text = raw_commit["description"]

        if not is_changed(raw_commit["commit_ID"], clean_text):
            log_action("Dev Agent", "Skipped unchanged commit", raw_commit["commit_ID"])
            continue

        # Check if feature exists before processing
        if not feature_status(workspace_id, feature_id):
            log_action(
                "Dev Agent",
                f"Feature {feature_id} not found in workspace {workspace_id}. Skipping.",
                raw_commit["commit_ID"],
            )
            continue

        embedding = get_embedding(clean_text)
        if not embedding:
            log_action(
                "Dev Agent",
                "No updates - nothing new to store",
                raw_commit["commit_ID"],
            )
            continue

        metadata = {
            "feature_id": feature_id,
            "title": raw_commit["title"],
            "feature_description": raw_commit["feature_description"],
            "commit_ID": raw_commit["commit_ID"],
            "author": raw_commit["author"],
        }

        store_vector(collection, clean_text, metadata, embedding)
        update_cache(raw_commit["commit_ID"], "commit_ID", clean_text)
        log_action("Dev Agent", "Stored new commit", str(metadata))
        update_commit_status(workspace_id, feature_id, raw_commit["commit_ID"], "Done")

        updated_commits.append(raw_commit)

    if not updated_commits:
        return state

    return {**state, "code_links": updated_commits}
