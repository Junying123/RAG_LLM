from llama_index.llms.ollama import Ollama
from llama_parse import LlamaParse
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, PromptTemplate
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from pydantic import BaseModel
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.query_pipeline import QueryPipeline
from prompts import context, code_parser_template

from dotenv import load_dotenv
import os
import ast




llm = Ollama(model="llama3", request_timeout=100000.0)

parser = LlamaParse(
    api_key="llx-kR0W83hinhfvdQeVHnITpwZUw8URXugzjSTC6AJDWYfYrif2",  # can also be set in your env as LLAMA_CLOUD_API_KEY
    result_type="markdown"  # "markdown" and "text" are available
)

file_extractor = {".pdf": parser}
documents = SimpleDirectoryReader("./data", file_extractor=file_extractor).load_data()

embed_model = resolve_embed_model("local:BAAI/bge-m3")
vector_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
query_engine = vector_index.as_query_engine(llm=llm)

# result = query_engine.query("What are some of the routes in the api?")
# print(result)

###TEST OUTPUTS###

#The API supports the following operations:
#* POST /items: Create a new item
#* GET /items: Retrieve all items
#* GET /items/<item_id>: Retrieve a single item by its ID
#* PUT /items/<item_id>: Update an existing item by its ID
#* DELETE /items/<item_id>: Delete an item by its ID


tools = [
    QueryEngineTool(
        query_engine=query_engine,
        metadata=ToolMetadata(
            name="api_documentation",
            description="this gives documentation about code for an API. Use this for reading docs for the API",
        ),
    ),
    
]



agent = ReActAgent.from_tools(tools, llm=llm, verbose=True, context=context)

class CodeOutput(BaseModel):
    code: str
    description: str
    filename: str

parser = PydanticOutputParser(CodeOutput)
json_prompt_str = parser.format(code_parser_template)
json_prompt_tmpl = PromptTemplate(json_prompt_str)
output_pipeline = QueryPipeline(chain=[json_prompt_tmpl, llm])

# pipeline = QueryPipeline.from_agent_and_tools(agent=agent, tools=tools, output_parser=output_parser)
while (prompt := input("Enter a prompt (q to quit): ")) != "q":
   # retry handler
   retries = 0
   
   while retries < 3:
        try:
            result = agent.query(prompt)
            next_result = output_pipeline.run(response=result)
            # print(next_result)
            cleaned_json = ast.literal_eval(str(next_result).replace("assistant:", ""))
        except Exception as e:
            print(f"Error Occurred, retry # {retries}:", e)
            retries += 1
   # if retries if failed to generate code in json format
   if retries >=3 :
        print("Unable to process request, try again")
        continue
   
   print("Code generated")
   print(cleaned_json["code"])
   print("\n\nDescription:", cleaned_json["description"])

   filename = cleaned_json["filename"]

   try:
       with open(os.path.join("output", filename), "w") as f:
            f.write(cleaned_json["code"])
       print("Saved file", filename)
   except:
       print("Error saving file...") 
    
   # prompt : 
   # read the contents of test.py and write a python script that calls the post endpoint to make a new item
   