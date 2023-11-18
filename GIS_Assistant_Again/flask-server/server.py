from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI
import json
import ast
import time
from collections import defaultdict

app = Flask(__name__)

PROMPT = "Annotate the location of the building with the largest area using the buildings file"

client = OpenAI(api_key='OPENAI_API_KEY_HERE')
assistant = client.beta.assistants.retrieve("ASSISTANT_ID_HERE")

thread = client.beta.threads.create()

  
CORS(app, resources={r'/api/*': {'origins': '*'}})
@app.route("/api/send_message", methods=['GET', 'POST'])
def send_message():
  message = request.json['message']
  
  thread_message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content= message
  )
  
  run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
  )


  while run.status not in ["completed", "failed", "requires_action"]:
    time.sleep(1)
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    print(run.status)
  tools_to_call = run.required_action.submit_tool_outputs.tool_calls
  tool_output_array = []
  map_annotation_data = defaultdict(int)
  for tool_to_call in tools_to_call:
    tool_call_id = tool_to_call.id
    function_name = tool_to_call.function.name
    function_arg = tool_to_call.function.arguments
    print("Tool ID: " + tool_call_id)
    print("Function to call: " + function_name)
    print("Parameters to use: " + function_arg)
    # TO DO call the API matching the functionname and return the output
    if function_name == "get_map_coords":
      # Parse the JSON string into a Python dictionary
      data = json.loads(function_arg)
      # Extract the string containing the float values
      float_values_str = data['list_of_points']
      # Split the string by comma to separate the float values

      points_list = ast.literal_eval(float_values_str)
      if data.get('building_names') is not None:
        map_annotation_data['building_name'] = data['building_names']
      map_annotation_data['list_of_points'] = points_list

      # Convert the string values to float and then to int
      print(points_list[0])


      output = True
    tool_output_array.append({"tool_call_id": tool_call_id, "output":output})
  run = client.beta.threads.runs.submit_tool_outputs(
    thread_id=thread.id,
    run_id=run.id,
    tool_outputs=tool_output_array
  )
  while run.status not in ["completed", "failed", "requires_action"]:
    time.sleep(1)

    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    print(run.status)
  messages = client.beta.threads.messages.list(
    thread_id=thread.id
  )
  
  recent = ""
  for each in messages:
    recent += each.content[0].text.value
    break
    #print(each)
    print(each.role + " : " + each.content[0].text.value)
    print("================")
  print("recent", recent)
  response = jsonify({'text_response': recent, 'annotation_data': map_annotation_data})
  response.headers.add('Access-Control-Allow-Origin', '*')
  return response
# make a response formatted as "text output", "what needs to be outputted on to the map"












# Have a method here that takes in calls from frontend
if __name__ == "__main__":
    app.run(debug=True)