from openai import OpenAI
import json

from tools import get_weather, run_command, read_file, write_file

client = OpenAI(
    api_key="",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


available_tools={
    "get_weather":get_weather,
    "run_command":run_command,
    "read_file":read_file,
    "write_file":write_file
}

SYSTEM_PROMPT = """
You are a smart helpful AI assistant that helps user in solving their queries.
You work on plan, action, observe, output mode.

For the given user query and available tools, plan the step by step execution, based on the planning,select the relevant tool from the available tools. And, based on the tool selection, you perform an action to call the tool.

Wait for the observation and based on the observation from the tool call, resolve the user query.

Rules:
- Follow the Output JSON format.
- Always perfom one step at a time and wait for next input
- Carefully analyze the user query 
- If more information is required from the user to proceed, respond with step: "follow_up" and ask a clear follow-up question in the content.

Output JSON Format:
{
    "step":"string", // One of: plan, action, observe, output, follow_up
    "content":"string",
    "function":"The name of function if the step is 'action'. Only include this field if step is 'action'",
    "input":"The input parameter for the 'function'. Only include this field if function field is present"
}

Available Tools:
- "get_weather": Takes a city name as an input and returns the current weather for that city.
- "run_command": Takes linux command as input and run it and returns the output of the command.
- "read_file": Takes path as input and reads the file and return the file's content or err message if occured.
- "write_file":" Takes the path of the file and content that is to be written as input. Writes the given content to a file at the specified path. Overwrites the file if it already exists. Returns success or error message.

For all other file or system operations not handled by read_file or write_file, use run_command.

Example:
User Query: What is the weather of Lucknow?
Output: {"step":"plan", "content":"The user is interested in weather data of lucknow"}
Output: {"step":"plan", "content":"From the available tools, I should call get_weather}
Output: {"step":"action", "function":"get_weather", "input":"lucknow"}
Output: {"step":"observe", "content":"24"}
Output: {"step":"output", "content":"The weahter for lucknow seems to be 24 degrees celsius"}

Example:
User Query: What is the weather?
Output: {"step":"plan", "content":"The user is asking for the weather but has not specified a city. I need to ask the user for the city to get the weather"}
Output: {"step":"follow_up", "content":"Could you please specify the city for which you want to know the weather?"}

Example:
User Query: Show me what's inside hello.txt
Output: {"step":"plan", "content":"The user wants to read the contents of hello.txt"}
Output: {"step":"plan", "content":"From the available tools, I should call read_file"}
Output: {"step":"action", "function":"read_file", "input":"hello.txt"}
Output: {"step":"observe", "content":"Hello from Python!"}
Output: {"step":"output", "content":"The contents of hello.txt are: Hello from Python!"}

Example:
User Query: Write 'Welcome to my app' in file welcome.txt that is in current directory
Output: {"step":"plan", "content":"The user wants to write some content into welcome.txt in the current directory. First, I will check if the file exists."}
Output: {"step":"action", "function":"run_command", "input":"ls"}
Output: {"step":"observe", "content":"app.js  index.html  welcome.txt  README.md"}
Output: {"step":"plan", "content":"Since welcome.txt is present, I will write the content to this file."}
Output: {"step":"action", "function":"write_file", "input":{"path":"welcome.txt", "content":"Welcome to my app"}}
Output: {"step":"observe", "content":"written to welcome.txt"}
Output: {"step":"output", "content":"Successfully wrote 'Welcome to my app' to welcome.txt"}

Example:
User Query: Write 'Welcome to my app' in file welcome.txt that is in current directory
Output: {"step":"plan", "content":"The user wants to write some content into welcome.txt in the current directory. First, I will check if the file exists."}
Output: {"step":"action", "function":"run_command", "input":"ls"}
Output: {"step":"observe", "content":"app.js  index.html  README.md"}
Output: {"step":"follow_up", "content":"I couldn't find 'welcome.txt' in the current directory. Do you want me to create it here, or please specify the path where I should write the file?"}

Example:
User Query: Create a new React app folder and modify its homepage to have an input field that displays whatever the user types.
{"step":"plan","content":"The user wants to create a React app with an input field that displays typed text. First, I need to know the folder name for the new React app."} 
{"step":"follow_up","content":"What should be the name of the React app folder where I will create the project?"}
{"step":"plan","content":"Creating a React app in folder 'myApp' and modifying myApp/src/App.jsx with input display component."}
{"step":"action","function":"run_command","input":"npm create vite@latest myApp"}
{"step":"observe","content":"Cannot create a project named "myApp" because of npm naming restrictions:..."}
{"step":"plan","content":"There is an error while creating react app because of naming convention, have to retry and the name should be lowercase."}
{"step":"follow_up","content":"name of react app must be in lowercase, please choose another."}
{"step":"plan","content":"Creating a React app in folder 'myapp' and modifying myapp/src/App.jsx with input display component."}
{"step":"action","function":"run_command","input":"npm create vite@latest myapp"}

{"step":"action","function":"write_file","input":{"path":"myapp/src/App.js","content":"import React, { useState } from 'react';\n\nfunction App() {\n  const [inputValue, setInputValue] = useState('');\n\n  return (\n    <div className=\"App\">\n      <input type=\"text\" value={inputValue} onChange={e => setInputValue(e.target.value)} />\n      <p>You typed: {inputValue}</p>\n    </div>\n  );\n}\n\nexport default App;"}}

{"step":"observe","content":"Updated myapp/src/App.js with input display component."}
{"step":"output","content":"Created React app in folder 'myapp' and updated App.js to include an input field that displays what the user types."}


Example:
User Query: Change the homepage of the React app in folder helo to have an input field and a submit button.
{"step":"plan", "content":"The user wants to modify the homepage of the React app inside the 'helo' folder to include an input field and a submit button."}
{"step":"plan", "content":"In a react app, the homepage is generally found at src/app.jsx, so the file is likely to be 'helo/src/app.jsx'."}
{"step":"plan", "content":"I will create a simple React component code snippet with an input and a submit button and overwrite 'helo/src/app.jsx' using the write_file tool."}

{"step":"action", "function":"write_file", "input":{
  "path":"helo/src/app.js",
  "content":"import React, { useState } from 'react';\n\nfunction App() {\n  const [inputValue, setInputValue] = useState('');\n\n  const handleSubmit = () => {\n    alert(`Submitted: ${inputValue}`);\n  };\n\n  return (\n    <div style={{ padding: '20px' }}>\n      <input \n        type=\"text\" \n        placeholder=\"Enter text\" \n        value={inputValue} \n        onChange={(e) => setInputValue(e.target.value)} \n      />\n      <button onClick={handleSubmit}>Submit</button>\n    </div>\n  );\n}\n\nexport default App;\n"
}}

{"step":"observe", "content":"Written to helo/app.js"}
{"step":"output", "content":"Successfully updated 'helo/app.js' with an input field and submit button component."}




"""

message = [
    {"role":"system", "content":SYSTEM_PROMPT},
]


while True:
    query = input("> ")
    message.append({"role":"user", "content":query})

    while True:
        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            response_format={"type":"json_object"},
            messages=message
        )
    
        message.append({"role":"assistant", "content":response.choices[0].message.content})
        parsed_response = json.loads(response.choices[0].message.content)

        if parsed_response.get("step") == "plan":

            print(f"🧠: {parsed_response.get("content")}")
            continue
        if parsed_response.get("step") == "follow_up":
            print(f"🤔: {parsed_response.get('content')}")
            user_input = input("> ")
            message.append({"role":"user", "content": user_input})
        
            continue
        if parsed_response.get("step") == "action":
            print(f"🤖: calling function-> {parsed_response.get("function")} and input-> {parsed_response.get("input")}")
            
            tool_name = parsed_response.get("function")
        
            if tool_name == 'write_file':
                tool_input = parsed_response.get("input")
                input_path = tool_input.get("path")
                input_content = tool_input.get("content") 

                tool_res = available_tools[tool_name](input_path, input_content)

            else:
                tool_input = parsed_response.get("input")   
                tool_res = available_tools[tool_name](tool_input)



            message.append({"role":"user", "content":json.dumps({"step":"observe", "content":tool_res})})
            continue
        if parsed_response.get("step") == "output":
            print(f"OUTPUT: {parsed_response.get("content")}")
            break






print(response.choices[0].message.content)

