from store.audit_log import log_action
from store.qdrant_store import init_collection, store_vector
from store.embedder import get_embedding
from utils.delta_checker import is_changed, update_cache
from state.trace_state import TraceState
from store.postgres_store import feature_status, update_test_status


def qa_agent_step(state: TraceState) -> TraceState:
    workspace_id = state["workspace_id"]
    collection = workspace_id
    init_collection(collection)

    updated_tests = []

    for raw_test in state.get("test_links", []):
        feature_id = raw_test["feature_id"]
        commit_id = raw_test["commit_ID"]
        clean_text = raw_test["description"]

        if not is_changed(raw_test["test_name"], clean_text):
            log_action("QA Agent", "Skipped unchanged test", raw_test["test_name"])
            continue

        # Check feature exists
        if not feature_status(workspace_id, feature_id):
            log_action(
                "QA Agent",
                f"Feature {feature_id} not found in workspace {workspace_id}. Skipping.",
                raw_test["test_name"],
            )
            continue

        # Check commit is done before proceeding
        if not feature_status(
            workspace_id, feature_id, require_commit_done=True, commit_ID=commit_id
        ):
            log_action(
                "QA Agent",
                f"Feature {feature_id} exists but commit {commit_id} is pending. Skipping.",
                raw_test["test_name"],
            )
            continue

        embedding = get_embedding(clean_text)
        if not embedding:
            log_action("QA Agent", "No embedding", raw_test["test_name"])
            continue

        metadata = {
            "feature_id": feature_id,
            "title": raw_test["title"],
            "feature_description": raw_test["feature_description"],
            "commit_ID": commit_id,
            "test_name": raw_test["test_name"],
            "test_status": raw_test["test_status"],
            "author": raw_test["author"],
        }

        store_vector(collection, clean_text, metadata, embedding)
        update_cache(raw_test["test_name"], "test", clean_text)
        log_action("QA Agent", "Stored new test", str(metadata))
        update_test_status(
            workspace_id,
            feature_id,
            commit_id,
            raw_test["test_name"],
            raw_test["test_status"],
        )

        updated_tests.append(raw_test)

    if not updated_tests:
        return state

    return {**state, "test_links": updated_tests}
