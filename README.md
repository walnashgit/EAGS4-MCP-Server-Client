# MCP Server with Gemini AI Integration

This project implements a Model Context Protocol (MCP) server with Gemini AI integration, allowing users to perform various mathematical operations and complex tasks through natural language commands.

## Features

- **Mathematical Operations**
  - Basic arithmetic (add, subtract, multiply, divide)
  - Advanced math (power, square root, cube root)
  - Special functions (factorial, log, trigonometric functions)
  - List operations (sum of list, exponential sum)

- **String Processing**
  - Convert strings to ASCII values
  - Process character arrays

- **Keynote Integration**
  - Open Keynote application
  - Draw rectangles with custom dimensions
  - Add text to shapes

- **AI-Powered Task Execution**
  - Natural language processing using Gemini AI
  - Iterative problem solving
  - Automatic tool selection based on user queries

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- macOS (for Keynote integration)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

## Project Structure

### Core Components
- `mcp_server.py`: Contains the MCP server implementation and tool definitions
- `models/data_model.py`: Pydantic models for tool inputs and outputs
- `.env`: Configuration file for API keys
- `requirements.txt`: Project dependencies

### Client Architecture

The client is built using a modular, four-layer architecture that follows a cognitive workflow:

1. **Perception Layer** (`perception.py`)
   - Extracts structured information from user input
   - Identifies objectives, objects, and tool hints
   - Uses Gemini AI to understand user intent

2. **Memory Layer** (`memory.py`)
   - Stores and retrieves factual information
   - Maintains context across the conversation
   - Provides relevant past information to improve decisions

3. **Decision Layer** (`decision.py`)
   - Takes perception and memory to generate plans
   - Determines whether to use tools or provide final answers
   - Creates structured function calls for tool execution

4. **Action Layer** (`action.py`)
   - Executes tool calls through the MCP session
   - Parses function calls and handles errors
   - Returns structured results for further processing

These layers are orchestrated by the main agent (`agent.py`), which manages the cognitive loop and user interaction.

## Usage

You can start the application in two ways:

### Option 1: Start Server and Client Separately
1. Start the MCP server in one terminal with SSE (default host 127.0.0.1 and port 7172):
```bash
python mcp_server.py sse
```
or

```bash
python mcp_server.py sse --host=127.0.0.2 --port=8383
```

2. In another terminal, run the client application with the new architecture:
```bash
python agent.py local
```
or

```bash
python agent.py local --host=127.0.0.2 --port=8383
```

### Option 2: Start Client Only (Recommended)
The client application can automatically start the server if it's not already running. Simply run:
```bash
python agent.py
```

The client will:
1. Check if the server is running
2. Start the server if needed
3. Establish connection automatically
4. Prompt for your preferences and query

### Using the Application
1. The system will first ask for some facts about you to establish context.
2. Enter your query when prompted. Examples:
   - "Add 5 and 3"
   - "Find the ASCII values of characters in INDIA"
   - "Start keynote app and draw a rectangle of size 300x400"
   - "Calculate the factorial of 5"

3. The system will:
   - Perceive your request
   - Retrieve relevant memories
   - Make decisions on which tools to use
   - Take actions and provide results
   - Continue the conversation until completion

4. Type 'exit' to quit the application.

## Cognitive Architecture Flow

The application follows this processing flow:

1. **Input** → User's natural language query
2. **Perception** → Extracts structured information (objectives, entities)
3. **Memory** → Retrieves relevant past information
4. **Decision** → Generates plan based on perception and memory
5. **Action** → Executes tool calls if needed
6. **Memory Update** → Stores results for future reference
7. **Loop** → Continues until a final answer is reached

This cognitive loop mirrors human decision-making processes, allowing for more contextual and coherent interactions.

## Prompt Improvements

In this branch, the prompt has been enhanced to be more structured and accurate, incorporating the following properties:

- **Explicit Reasoning**: The prompt encourages clear and logical reasoning in responses.
- **Structured Output**: Responses are formatted in a way that is easy to read and understand.
- **Tool Separation**: Different tools and functionalities are clearly delineated for better usability.
- **Conversation Loop**: The prompt supports an interactive dialogue, allowing for back-and-forth communication.
- **Instructional Framing**: Instructions are framed in a way that guides the user effectively.
- **Internal Self-Checks**: The system performs checks to ensure the reasoning process is sound.
- **Reasoning Type Awareness**: The prompt is aware of different types of reasoning required for various tasks.
- **Fallbacks**: There are mechanisms in place to handle unexpected inputs or errors gracefully.
- **Overall Clarity**: The prompt is highly structured and rigorous, making it excellent for guiding LLMs through safe, interpretable, step-by-step reasoning with tool use. There is a strong emphasis on formatting and reasoning discipline.

These improvements aim to enhance the user experience and ensure that the system operates more effectively and safely. 
  
## Demo

Watch a demo of the MCP Server with Gemini AI integration in action:

[![MCP Server Demo](https://img.youtube.com/vi/N36YqaE25wA/0.jpg)](https://youtu.be/G1thktyJHnQ)

Click the image above to watch the demo video on YouTube. 

## Error Handling

The system includes comprehensive error handling:
- Timeout handling for AI responses
- Type conversion validation
- Tool availability checking
- Parameter validation
- Graceful fallbacks at each layer of the architecture

## Debugging

Debug information is printed to the console, including:
- Tool execution details
- Parameter processing
- Result formatting
- Error messages and stack traces
- Cognitive process flow with timestamped logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini AI for natural language processing capabilities
- MCP framework for tool management
- Python community for various libraries used in this project 

