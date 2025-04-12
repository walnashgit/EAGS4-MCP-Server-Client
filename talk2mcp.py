import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
from google import genai
from concurrent.futures import TimeoutError
from functools import partial
import json
import sys
from mcp.client.sse import sse_client

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

max_iterations = 20
last_response = None
iteration = 0
iteration_response = []

async def generate_with_timeout(client, prompt, timeout=10):
    """Generate content with a timeout"""
    print("Starting LLM generation...")
    try:
        # Convert the synchronous generate_content call to run in a thread
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        print("LLM generation completed")
        return response
    except TimeoutError:
        print("LLM generation timed out!")
        raise
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        raise

def reset_state():
    """Reset all global variables to their initial state"""
    global last_response, iteration, iteration_response
    last_response = None
    iteration = 0
    iteration_response = []

async def main(local: bool):
    reset_state()  # Reset at the start of main
    print("Starting main execution...")
    try:
        # Create a single MCP server connection
        print("Establishing connection to MCP server...")
        if local:
            print("connecting with server at localhost...")
            # async with sse_client("http://127.0.0.1:7171/mcp") as (read, write):
            #     print("connected with server at localhost...")
            #     await client_main(read, write)
            # print("connecting with server at localhost...")
            # server_params = StdioServerParameters(
            #     command="uv",
            #     args=["/Users/avinashkumaragarwal/Me/EAGV1/S5MCP-OpenDesktopApp/venv/bin/uv, args=run,--with,mcp,mcp,run,mcp_server.py"]
            # )
            # print("connected with server at localhost...")
            # async with stdio_client(server_params) as (read, write):
            #     await client_main(read, write)
        else:
            server_params = StdioServerParameters(
                command="python",
                args=["mcp_server.py"]
            )
            async with stdio_client(server_params) as (read, write):
                await client_main(read, write)
            
    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        reset_state() 
        
async def client_main(read, write):
    print("Connection established, creating session...")
    async with ClientSession(read, write) as session:
        print("Session created, initializing...")
        await session.initialize()
        
        # Get available tools
        print("Requesting tool list...")
        tools_result = await session.list_tools()
        tools = tools_result.tools
        print(f"Successfully retrieved {len(tools)} tools")

        # Create system prompt with available tools
        print("Creating system prompt...")
        print(f"Number of tools: {len(tools)}")
        
        try:
            # First, let's inspect what a tool object looks like
            # if tools:
            #     print(f"First tool properties: {dir(tools[0])}")
            #     print(f"First tool example: {tools[0]}")
            
            tools_description = []
            for i, tool in enumerate(tools):
                try:
                    # Get tool properties
                    params = tool.inputSchema
                    desc = getattr(tool, 'description', 'No description available')
                    name = getattr(tool, 'name', f'tool_{i}')
                    
                    # Format the input schema in a more readable way
                    if 'properties' in params:
                        param_details = []
                        for param_name, param_info in params['properties'].items():
                            param_type = param_info.get('type', 'unknown')
                            param_details.append(f"{param_name}: {param_type}")
                        params_str = ', '.join(param_details)
                    else:
                        params_str = 'no parameters'

                    tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                    tools_description.append(tool_desc)
                    print(f"Added description for tool: {tool_desc}")
                except Exception as e:
                    print(f"Error processing tool {i}: {e}")
                    tools_description.append(f"{i+1}. Error processing tool")
            
            tools_description = "\n".join(tools_description)
            print("Successfully created tools description")
        except Exception as e:
            print(f"Error creating tools description: {e}")
            tools_description = "Error loading tools"
        
        print("Created system prompt...")
        
        system_prompt = f"""You are an intelligent AI agent capable of solving complex mathematical problems and answering user queries through iterative reasoning. You have access to the following tools:

{tools_description}
🧠 Reasoning Instructions:

Think step-by-step before answering.

Explicitly identify the type of reasoning you are using at each step (e.g., arithmetic, logic, lookup).

ALWAYS provide reasoning before starting to solve a problem.

Provide reasoning for intermediate steps whereever necessary.

Self-verify your intermediate steps before proceeding.

If uncertain or a tool fails, attempt a fallback approach and note it.

📤 Response Format:

Respond with EXACTLY ONE line, and use only one of the formats below (no extra text):

For reasoning step:
FUNCTION_CALL: {{"name":"show_reasoning", "params":[{{"param": ["1. [arithmetic] First, solve inside parentheses: 2 + 3", "2. [arithmetic] Then multiply the result by 4"]}}]}}

For other tool use:
FUNCTION_CALL: {{"name":"function_name","params":[{{"param":"p1"}},{{"param":"p2"}}]}}

For final output:
FINAL_ANSWER: [answer]

📝 Example Outputs:

FUNCTION_CALL: {{"name":"add","params":[{{"param":"2"}}, {{"param":"3"}}]}}

FINAL_ANSWER: [42]

Example:
Query: Solve (2 + 3) * 4
Assistant: FUNCTION_CALL: {{"name":"show_reasoning", "params":[{{"param": ["1. [arithmetic] First, solve inside parentheses: 2 + 3", "2. [arithmetic] Then multiply the result by 4"]}}]}}
Query: Result is Reasoning shown. What should I do next?
Assistant: FUNCTION_CALL: {{"name":"add","params":[{{"param":"2"}}, {{"param":"3"}}]}}
Query: Result is 5. What should I do next?
Assistant: FUNCTION_CALL: {{"name":"multiply","params":[{{"param":"5"}}, {{"param":"4"}}]}} 
User: Result is 20. What should I do next?
Assistant: FINAL_ANSWER: [20]

🧾 Additional Rules:

Do not repeat function calls with the same parameters.

Do not change the name of the parameter 'param' in FUNCTION_CALL when you respond.

Only give FINAL_ANSWER when all reasoning and computation are complete.

In case of tool failure or ambiguous input, output:
FALLBACK: [brief description of the issue and next step]"""

        # query = """Find the ASCII values of characters in INDIA and then take the sum of exponentials of those values. 
        #  Then start keynote app, draw a rectangle of size 300x400 and add the text "MCP server rocks -" and the value that you just calculated. """
        # query = """Start keynote app, draw a rectangle of size 300x400 and add the text "MCP server rocks!" """
        # Get user input for the query
        print("\nEnter your query (or 'exit' to quit):")
        query = input("> ")
        
        if query.lower() == 'exit':
            print("Exiting...")
            return
            
        print("Starting iteration loop...")
        
        # Use global iteration variables
        global iteration, last_response
        
        while iteration < max_iterations:
            print(f"\n--- Iteration {iteration + 1} ---")
            if last_response is None:
                current_query = query
            else:
                current_query = current_query + "\n\n" + " ".join(iteration_response)
                current_query = current_query + "  What should I do next?"

            # Get model's response with timeout
            print("Preparing to generate LLM response...")
            prompt = f"{system_prompt}\n\nQuery: {current_query}"
            try:
                response = await generate_with_timeout(client, prompt)
                response_text = response.text.strip()
                print(f"LLM Response: {response_text}")
                
                # Find the FUNCTION_CALL line in the response
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line.startswith("FUNCTION_CALL:"):
                        response_text = line
                        break
                
            except Exception as e:
                print(f"Failed to get LLM response: {e}")
                break


            if response_text.startswith("FUNCTION_CALL:"):
                _, function_info = response_text.split(":", 1)
                function_info_json = json.loads(function_info)
                func_name = function_info_json['name']
                params = function_info_json['params']
                # parts = [p.strip() for p in function_info.split("|")]
                # func_name, params = parts[0], parts[1:]
                
                # print(f"\nDEBUG: Raw function info: {function_info}")
                # print(f"DEBUG: Split parts: {parts}")
                # print(f"DEBUG: Function name: {func_name}")
                # print(f"DEBUG: Raw parameters: {params}")
                
                try:
                    # Find the matching tool to get its input schema
                    tool = next((t for t in tools if t.name == func_name), None)
                    if not tool:
                        print(f"DEBUG: Available tools: {[t.name for t in tools]}")
                        raise ValueError(f"Unknown tool: {func_name}")

                    # print(f"DEBUG: Found tool: {tool.name}")
                    # print(f"DEBUG: Tool schema: {tool.inputSchema}")

                    # Prepare arguments according to the tool's input schema
                    arguments = {}
                    schema_properties = tool.inputSchema.get('properties', {})
                    # print(f"DEBUG: Schema properties: {schema_properties}")

                    for param_name, param_info in schema_properties.items():
                        if not params:  # Check if we have enough parameters
                            raise ValueError(f"Not enough parameters provided for {func_name}")
                            
                        param = params.pop(0)  # Get and remove the first parameter
                        value = param['param']
                        param_type = param_info.get('type', 'string')
                        
                        # print(f"DEBUG: Converting parameter {param_name} with value {value} to type {param_type}")
                        
                        # Convert the value to the correct type based on the schema
                        if param_type == 'integer':
                            arguments[param_name] = int(value)
                        elif param_type == 'number':
                            arguments[param_name] = float(value)
                        elif param_type == 'array':
                            # Handle array input
                            # print(f"DEBUG: Handling array arguments")
                            if isinstance(value, str):
                                value = value.strip('[]').split(',')
                            # arguments[param_name] = [int(x.strip()) for x in value]
                            # arguments[param_name] = [int(x) for x in value]
                            arguments[param_name] = [try_parse_int(x) for x in value]
                        else:
                            arguments[param_name] = str(value)

                    # print(f"DEBUG: Final arguments: {arguments}")
                    print(f"DEBUG: Calling tool {func_name}")
                    
                    result = await session.call_tool(func_name, arguments=arguments)
                    # print(f"DEBUG: Raw result: {result}")
                    
                    # Get the full result content
                    if hasattr(result, 'content'):
                        # print(f"DEBUG: Result has content attribute")
                        # Handle multiple content items
                        if isinstance(result.content, list):
                            iteration_result = [
                                item.text if hasattr(item, 'text') else str(item)
                                for item in result.content
                            ]
                        else:
                            iteration_result = str(result.content)
                    else:
                        print(f"DEBUG: Result has no content attribute")
                        iteration_result = str(result)
                        
                    print(f"DEBUG: Final iteration result: {iteration_result}")
                    
                    # Format the response based on result type
                    if isinstance(iteration_result, list):
                        result_str = f"[{', '.join(iteration_result)}]"
                    else:
                        result_str = str(iteration_result)
                    
                    iteration_response.append(
                        f"In the {iteration + 1} iteration you called {func_name} with {arguments} parameters, "
                        f"and the function returned {result_str}."
                    )
                    last_response = iteration_result

                except Exception as e:
                    print(f"DEBUG: Error details: {str(e)}")
                    print(f"DEBUG: Error type: {type(e)}")
                    import traceback
                    traceback.print_exc()
                    iteration_response.append(f"Error in iteration {iteration + 1}: {str(e)}")
                    break

            elif "FINAL_ANSWER:" in response_text:
                print("\n=== Agent Execution Complete ===")
                break

            iteration += 1 # Reset at the end of main

def try_parse_int(x):
    try:
        return int(x)
    except ValueError:
        return x

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "local":
        asyncio.run(main(True))
    else:
        asyncio.run(main(False))
    
    
