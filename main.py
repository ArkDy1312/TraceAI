from ui.gradio_ui import dashboard
from utils.data_ingestion import run_trace

if __name__ == "__main__":
    run_trace()
    dashboard.launch(server_name="0.0.0.0", server_port=8000)
