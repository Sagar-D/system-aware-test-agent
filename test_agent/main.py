import gradio as gr
from test_agent import config
from test_agent.schemas.agent_schemas.prd_agent_schemas import PrdAnalyzerAgentState, PrdDocument
from test_agent.document.document_processor import process_document
from test_agent.agents.prd_agent.prd_analyzer_agent import PrdAnalyzerAgent
from test_agent.db.setup import initialize_db

initialize_db()

def process_files(file: bytes):
    doc_id, doc_content = process_document(file=file)
    document = PrdDocument(id=doc_id, page_content=doc_content)
    
    agent_state = PrdAnalyzerAgentState(
        project_id= "PROJECT-1",
        release_id= "RELEASE-1",
        document=document
    )
    
    agent = PrdAnalyzerAgent()
    result = agent.invoke(state=agent_state)
    return []

def create_gradio_chat_interface():

    with gr.Blocks() as app:

        gr_state = gr.State({})
        with gr.Row():
            chatbot = gr.Chatbot(height=450, scale=10)

        with gr.Row():


            llm_platform = gr.Dropdown(
                choices=config.SUPPORTED_LLM_PLATFORMS,
                value=config.DEFAULT_LLM_PLATFORM,
                type="value",
                label="LLM Platform",
                multiselect=False,
            )
            msg = gr.Textbox(
                placeholder="Type your query here...", label="User Message:", scale=8
            )
            file = gr.File(
                file_count="single",
                type="binary",
                file_types=[".pdf"],
                height=80,
            )
            send = gr.Button("Send")


        send.click(
            fn=process_files,
            inputs=[file],
            outputs=[chatbot],
        )
        msg.submit(
            fn=process_files,
            inputs=[file],
            outputs=[chatbot],
        )

    return app

app = create_gradio_chat_interface()
app.launch()