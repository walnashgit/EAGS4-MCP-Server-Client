# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp.server import Server
from starlette.routing import Mount, Route
import uvicorn
from mcp import types
from PIL import Image as PILImage
import math
import sys
# from pywinauto.application import Application
# import win32gui
# import win32con
import time
import subprocess
from rich.console import Console
from rich.panel import Panel
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
# from win32api import GetSystemMetrics

console = Console()
# instantiate an MCP server client
mcp = FastMCP("Calculator", settings= {"host": "127.0.0.1", "port": 7172})

app = FastAPI()

# DEFINE TOOLS

#addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print("CALLED: add(a: int, b: int) -> int:")
    return int(a + b)

@mcp.tool()
def add_list(l: list) -> int:
    """Add all numbers in a list"""
    print("CALLED: add(l: list) -> int:")
    return sum(l)

# subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    print("CALLED: subtract(a: int, b: int) -> int:")
    return int(a - b)

# multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print("CALLED: multiply(a: int, b: int) -> int:")
    return int(a * b)

#  division tool
@mcp.tool() 
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    print("CALLED: divide(a: int, b: int) -> float:")
    return float(a / b)

# power tool
@mcp.tool()
def power(a: int, b: int) -> int:
    """Power of two numbers"""
    print("CALLED: power(a: int, b: int) -> int:")
    return int(a ** b)

# square root tool
@mcp.tool()
def sqrt(a: int) -> float:
    """Square root of a number"""
    print("CALLED: sqrt(a: int) -> float:")
    return float(a ** 0.5)

# cube root tool
@mcp.tool()
def cbrt(a: int) -> float:
    """Cube root of a number"""
    print("CALLED: cbrt(a: int) -> float:")
    return float(a ** (1/3))

# factorial tool
@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    print("CALLED: factorial(a: int) -> int:")
    return int(math.factorial(a))

# log tool
@mcp.tool()
def log(a: int) -> float:
    """log of a number"""
    print("CALLED: log(a: int) -> float:")
    return float(math.log(a))

# remainder tool
@mcp.tool()
def remainder(a: int, b: int) -> int:
    """remainder of two numbers divison"""
    print("CALLED: remainder(a: int, b: int) -> int:")
    return int(a % b)

# sin tool
@mcp.tool()
def sin(a: int) -> float:
    """sin of a number"""
    print("CALLED: sin(a: int) -> float:")
    return float(math.sin(a))

# cos tool
@mcp.tool()
def cos(a: int) -> float:
    """cos of a number"""
    print("CALLED: cos(a: int) -> float:")
    return float(math.cos(a))

# tan tool
@mcp.tool()
def tan(a: int) -> float:
    """tan of a number"""
    print("CALLED: tan(a: int) -> float:")
    return float(math.tan(a))

# @mcp.tool()
# def calculate(expression: str) -> TextContent:
#     """Calculate the result of an expression"""
#     console.print("[blue]FUNCTION CALL:[/blue] calculate()")
#     console.print(f"[blue]Expression:[/blue] {expression}")
#     try:
#         result = eval(expression)
#         console.print(f"[green]Result:[/green] {result}")
#         return TextContent(
#             type="text",
#             text=str(result)
#         )
#     except Exception as e:
#         console.print(f"[red]Error:[/red] {str(e)}")
#         return TextContent(
#             type="text",
#             text=f"Error: {str(e)}"
#         )

# mine tool
@mcp.tool()
def mine(a: int, b: int) -> int:
    """special mining tool"""
    print("CALLED: mine(a: int, b: int) -> int:")
    return int(a - b - b)

# reasoning tool
@mcp.tool()
def show_reasoning(steps: list) -> TextContent:
    """Show the step-by-step reasoning process"""
    console.print("[blue]FUNCTION CALL:[/blue] show_reasoning()")
    for i, step in enumerate(steps, 1):
        console.print(Panel(
            f"{step}",
            title=f"Step {i}",
            border_style="cyan"
        ))
    return TextContent(
        type="text",
        text="Reasoning shown"
    )

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    print("CALLED: create_thumbnail(image_path: str) -> Image:")
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def strings_to_chars_to_int(string: str) -> list[int]:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(string: str) -> list[int]:")
    return [int(ord(char)) for char in string]

@mcp.tool()
def int_list_to_exponential_sum(int_list: list) -> float:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(int_list: list) -> float:")
    return sum(math.exp(i) for i in int_list)

@mcp.tool()
def fibonacci_numbers(n: int) -> list:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(n: int) -> list:")
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]

@mcp.tool()
def open_keynote() -> bool:
    """Opens the keynote app and creates a new document in the macbook. Returns True if successful, False otherwise."""
    print("CALLED: open_keynote() -> bool")
    apple_script = '''
    tell application "Keynote"
        activate
        set thisDocument to make new document with properties {document theme:theme "White"}
        tell thisDocument
            set base slide of the first slide to master slide "Blank"
        end tell
    end tell
    '''
    result = subprocess.run(["osascript", "-e", apple_script],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print("Error:", result.stderr)
        return False
    print("Keynote opened and new document created.")
    return True

@mcp.tool()
def draw_rectangle_in_keynote(shapeWidth: int, shapeHeight: int) -> bool:
    """Draws a rectangle in keynote app of the privided size. Returns True if rectangle is drawn successfully, False otherwise."""
    print("CALLED: draw_rectangle_in_keynote(shapeWidth: int, shapeHeight: int) -> bool")
    apple_script = f'''
    tell application "Keynote"
        tell document 1
            set docWidth to its width
            set docHeight to its height
            set x to (docWidth - {{{shapeWidth}}}) div 2
            set y to (docHeight - {{{shapeHeight}}}) div 2
            tell slide 1
                set newRectangle to make new shape with properties {{position:{{x, y}}, width:{shapeWidth}, height:{shapeHeight}}}
            end tell
        end tell
    end tell
    '''
    result = subprocess.run(["osascript", "-e", apple_script],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print("Step 2 Error:", result.stderr)
        return False
    print("Step 2 completed: Rectangle drawn on the slide.")
    return True

@mcp.tool()
def add_text_to_keynote_shape(text: str) -> bool:
    """Adds a text to the shape drawn in keynote. Return True if text was added successfully, False otherwise."""
    print("CALLED: add_text_to_keynote_shape(text: str) -> bool")
    apple_script = f'''
    tell application "Keynote"
        tell document 1
            tell slide 1
                set the object text of the shape 1 to "{text}"
            end tell
        end tell
    end tell
    '''
    result = subprocess.run(["osascript", "-e", apple_script],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print("Step 3 Error:", result.stderr)
        return False
    print("Step 3 completed: Text added to the rectangle.")
    return True

# DEFINE RESOURCES

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"


# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
    print("CALLED: review_code(code: str) -> str:")


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

def start_sse():
    mcp_server = mcp._mcp_server  # noqa: WPS437
    import argparse
    from pdb import set_trace

    # set_trace()
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=7172, help='Port to listen on')
    args = parser.parse_args()
    print("SSE args set.")

    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)
    app.mount("/", starlette_app)

    uvicorn.run(app, host=args.host, port=args.port) 

@app.get("/")
def read_root():
    return {"Hello": "Worlddd"}

@app.get("/mcp")
async def get_capabilites():
    return await mcp.list_tools()


if __name__ == "__main__":
    # Check if running with mcp dev command
    print("STARTING")
    if len(sys.argv) > 1:
        if sys.argv[1] == "dev":
            print("STARTING without transport for dev server")
            mcp.run() 
        elif sys.argv[1] == "sse":
            sys.argv.remove("sse")
            print("STARTING sse server")
            start_sse()
     # Run without transport for dev server
    else:
        print("STARTING with stdio for direct execution")
        mcp.run(transport="stdio")
else: 
    print("starting sse...")
    start_sse()
        

 # Run with stdio for direct execution
