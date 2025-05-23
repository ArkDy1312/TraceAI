from typing import List, Optional, TypedDict


# Shared state structure
class TraceState(TypedDict):
    workspace_id: str
    feature_specs: Optional[List[dict]]
    code_links: Optional[List[dict]]
    test_links: Optional[List[dict]]
