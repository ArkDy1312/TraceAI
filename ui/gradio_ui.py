import gradio as gr
from store.hybrid_search import hybrid_search
from ui.graph_view import generate_trace_graph
from store.llm_chat import llm_call
from store.audit_reader import get_audit_logs
from store.audit_reader import get_manual_overrides
from utils.manual_updating import manual_update
from store.postgres_store import get_feature_id_title_pairs, get_commits_for_feature, get_tests_for_feature
import tempfile

teams = ["Alpha", "Beta", "Gamma", "Debug"]

def show_manual_overrides():
    return get_manual_overrides()

def show_logs():
    df = get_audit_logs()
    return df

def answer_and_graph(query: str, workspace_id: str, feature_id: str):
    try:
        feature_id = feature_id.split(" - ")[1]
        results, type = hybrid_search(query, workspace_id=workspace_id, feature_id=feature_id)

        # Construct context for LLM (top 5 docs)
        context_chunks = []
        for r in results:
            if r.get("payload", {}).get("text"):
                final_string = ""
                for k, v in r["payload"].items():
                    final_string += f"{k.replace('_', ' ').title()}: {v}\n"
                context_chunks.append(final_string)
            elif r.get("content"):
                context_chunks.append(r["content"])
        context = "\n\n".join(context_chunks[:5])

        # Generate answer using LLM
        llm_answer = llm_call(context=context, question=query)

        answer = f"### 🤖 LLM Answer:\n{llm_answer}\n\n---\n"

        # Step 4: Build exportable Markdown report
        report_md = f"# Traceability Report\n\n"
        report_md += f"**Workspace:** {workspace_id}\n\n"
        report_md += f"**Query:** {query}\n\n"
        # report_md += f"**Role:** {role}\n\n"
        report_md += f"**LLM Answer:**\n{llm_answer}\n\n"
        report_md += "## Linked Items (Top Results)\n"

        for r in results:
            for t in type:
                report_md += f"- **{t.upper()}**: {r['payload']['text']}\n"

        # Write to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w", encoding="utf-8")
        temp_file.write(report_md)
        temp_file.close()
        report_path = temp_file.name

        return answer, report_path

    except Exception as e:
        if not query.strip():
            return "⚠️ Please enter a question before submitting.", None
        else:
            return f"❌ Error: {str(e)}", "<p>Error generating graph.</p>", None
    
# Callback when workspace changes
def update_documents(workspace):
    return gr.update(choices=get_feature_id_title_pairs(workspace), value=None)

# Trace UI in Blocks
with gr.Blocks() as trace_ui:
    gr.Markdown("# LLM x Traceability Query Interface")
    gr.Markdown("Ask about features, commits, or tests. Powered by LangGraph, Qdrant & Ollama.")

    with gr.Row():
        # 🟦 Left side: Inputs
        with gr.Column(scale=1):
            workspace_input = gr.Dropdown(teams, label="Workspace/Team")
            feature_dropdown = gr.Dropdown(label="Features/Specs", choices=[], interactive=True)
            question_input = gr.Textbox(lines=2, placeholder="Ask something like: Was login tested?")
            submit_btn = gr.Button("Submit")

        # 🟨 Right side: Outputs
        with gr.Column(scale=2):
            answer_output = gr.Markdown(label="Answer")
            file_output = gr.File(label="Download Report (Markdown)")

    # Button click
    submit_btn.click(
        fn=answer_and_graph,
        inputs=[question_input, workspace_input, feature_dropdown],
        outputs=[answer_output, file_output]
    )

    # Dynamic document update
    workspace_input.change(
        fn=update_documents,
        inputs=workspace_input,
        outputs=feature_dropdown
    )

with gr.Blocks() as trace_graph_ui:
    gr.Markdown("## 📈 Traceability Graph Explorer")

    with gr.Row():
        workspace_input = gr.Dropdown(teams, label="Workspace/Team")
        feature_dropdown = gr.Dropdown(label="Feature", choices=[], interactive=True)
        generate_btn = gr.Button("Generate Trace Graph")
    graph_output = gr.HTML(label="Trace Graph")

    # 🔄 Update feature list when workspace is selected
    workspace_input.change(
        fn=update_documents,
        inputs=workspace_input,
        outputs=feature_dropdown
    )

    generate_btn.click(
        fn=generate_trace_graph,
        inputs=[workspace_input, feature_dropdown],
        outputs=graph_output
    )

log_ui = gr.Interface(
    fn=show_logs,
    inputs=[],
    outputs=gr.Dataframe(headers=["timestamp", "agent", "action", "details"]),
    title="🧾 Audit Log Viewer",
    description="See what each agent did and when.",
    flagging_mode="never"  # Hide the flag button
)

with gr.Blocks() as manual_ui:
    gr.Markdown("🔧 **Manual Trace Editor**")
    gr.Markdown("Manually update the commit or test for a feature.")

    with gr.Row():
        with gr.Column(scale=1):
            workspace_input = gr.Dropdown(teams, label="Workspace/Team")
            feature_dropdown = gr.Dropdown(label="Feature", choices=[], interactive=True)
            action_type = gr.Dropdown(["Commit", "Test"], label="Action Type", interactive=True)
            item_dropdown = gr.Dropdown(label="Commit/Test ID", choices=[], interactive=True)
            description_box = gr.Textbox(lines=2, label="Description")
            author_box = gr.Textbox(lines=1, label="Author")
            submit_btn = gr.Button("Update")

        with gr.Column(scale=1):
            result_output = gr.Textbox(label="Result")

    # Populate features when workspace changes
    workspace_input.change(
        fn=update_documents,
        inputs=workspace_input,
        outputs=feature_dropdown
    )

    # Populate commit/test IDs when action type or feature is selected
    def update_item_ids(workspace, feature_id, action):
        if action == "Commit":
            values = get_commits_for_feature(workspace, feature_id)
        elif action == "Test":
            values = get_tests_for_feature(workspace, feature_id)
        else:
            values = []
        
        return gr.update(choices=values, value=None)

    action_type.change(fn=update_item_ids, inputs=[workspace_input, feature_dropdown, action_type], outputs=item_dropdown)
    feature_dropdown.change(fn=update_item_ids, inputs=[workspace_input, feature_dropdown, action_type], outputs=item_dropdown)

    # On submit, run the update logic
    submit_btn.click(
        fn=manual_update,  # your function to apply update
        inputs=[workspace_input, feature_dropdown, action_type, item_dropdown, description_box, author_box],
        outputs=[result_output]
    )

override_ui = gr.Interface(
    fn=show_manual_overrides,
    inputs=[],
    outputs=gr.Dataframe(label="Manual Unlinks"),
    title="✍️ Manual Trace Log",
    description="See all manual feature → Test/Commit actions.",
    flagging_mode="never"
)

dashboard = gr.TabbedInterface(
    [trace_ui, trace_graph_ui, log_ui, manual_ui, override_ui],
    tab_names=["🧠 Trace Query", "🔍 Trace Graph Viewer", "🧾 Audit Logs", "🔧 Manual Editor", "✍️ Manual Log"]
)

