# llama_index
from llama_index.llms.openai import OpenAI
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool


llm = OpenAI(model="gpt-4o", api_key= 'sk-proj-qgueRmcPNpX0QJUpL9tCT3BlbkFJ9jcW0NJRrxxmG99NBcxS')

def generate_report():
    print("done")
    return "report generated"
    
report_generator = FunctionTool.from_defaults(
    fn=generate_report,
    name="report_generator",
    description="This tool can generate a PDF report from markdown text"
)

agent = ReActAgent.from_tools(
    tools=[
        report_generator,
        ],
    llm=llm,
    verbose=True
)

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    response = agent.chat(user_input)
    print("Agent: ", response)