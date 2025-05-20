from pyvis.network import Network
import networkx as nx
from store.postgres_store import get_graph_data

# Decide node color based on status
status_color = {
    "Passed": "green",
    "Failed": "red",
    "Pending": "gray",
    "Done": "blue",
}

def parse_feature_rows(rows):
    features = {
        "feature_id": [],
        "title": [],
        "description": [],
        "commits": [],
        "commit_status": [],
        "test_name": [],
        "test_status": []
    }

    if not rows:
        return features

    for feature_id, title, description, commit_id, commit_status, test_name, test_status in rows:
        # Append feature details
        features["feature_id"].append(feature_id)
        features["title"].append(title)
        features["description"].append(description)
        features["commits"].append(commit_id)
        features["commit_status"].append(commit_status)
        features["test_name"].append(test_name)
        features["test_status"].append(test_status)
    return features

def generate_trace_graph(workspace: str, feature: str):
    G = nx.DiGraph()

    graph_data = get_graph_data(workspace, feature)
    graph_data = parse_feature_rows(graph_data)

    for item in range(len(graph_data["feature_id"])):
        feature_id = graph_data["feature_id"][item]
        title = graph_data["title"][item]
        description = graph_data["description"][item]
        commit_id = graph_data["commits"][item]
        commit_status = graph_data["commit_status"][item]
        test_name = graph_data["test_name"][item]
        test_status = graph_data["test_status"][item]

        if commit_id is None:
            commit_id = ""
            commit_label=f"Commit: [{commit_status}]"
        else:
            commit_label=f"Commit: {commit_id}\n[{commit_status}]"
        if test_name is None:
            test_name = ""
            test_label=f"Test: [{test_status}]"
        else:
            test_label=f"Test: {test_name}\n[{test_status}]"

        G.add_node(
            feature_id,
            label=title,
            title=f"Feature ID: {feature_id}\n{description}",
            color="orange",
            url=f"https://example.com/feature/{feature_id}"
        )

        G.add_node(
            commit_id,
            label=commit_label,
            title="",
            color=status_color.get(commit_status),
            url=f"https://github.com/your-org/repo/commit/{commit_id}"
        )
        G.add_edge(feature_id, commit_id)

        G.add_node(
            test_name,
            label=test_label,
            title="",
            color=status_color.get(test_status),
            url=f"https://testrail.local/tests/{test_name}"
        )
        G.add_edge(commit_id, test_name)

    net = Network(directed=True, height="600px", width="100%", notebook=False)
    net.from_nx(G)
    net.show_buttons(filter_=['physics'])  # Optional toolbar

    html = net.generate_html()
    html = html.replace("'", "\"")
    final_html = f"""<iframe style="width: 100%; height: 600px;margin:0 auto" name="result" allow="midi; geolocation; microphone; camera; 
    display-capture; encrypted-media;" sandbox="allow-modals allow-forms 
    allow-scripts allow-same-origin allow-popups 
    allow-top-navigation-by-user-activation allow-downloads" allowfullscreen="" 
    allowpaymentrequest="" frameborder="0" srcdoc='{html}'></iframe>"""
    return final_html
