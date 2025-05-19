import os
import sys
import json
import subprocess
import openai
import re

openai.api_key = os.getenv("OPENAI_API_KEY")  # Make sure this is set

# MCP server command
MCP_SERVER_CMD = ["python3", "yahoo_finance_mcp_server.py"]


def start_mcp_server():
    """Launch MCP server subprocess with stdin/stdout communication"""
    proc = subprocess.Popen(
        MCP_SERVER_CMD,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    return proc


def call_mcp(proc, method: str, params: dict):
    if proc.poll() is not None:
        raise RuntimeError("MCP server has exited unexpectedly before receiving the request.")

    request = {
        "method": method,
        "params": params
    }

    print(f"🔧 Calling MCP tool: {method}({params})")

    try:
        proc.stdin.write(json.dumps(request) + "\n")
        proc.stdin.flush()
    except BrokenPipeError:
        raise RuntimeError("Failed to send request to MCP server: Broken pipe")

    # Read response
    response_line = proc.stdout.readline().strip()
    try:
        return json.loads(response_line)
    except json.JSONDecodeError:
        raise RuntimeError(f"Invalid JSON response from MCP: {response_line}")


def extract_tool_blocks(response: str):
    """Extract tool blocks from model response"""
    tool_calls = []
    matches = re.findall(r"<tool>(.*?)</tool>", response, re.DOTALL)
    for match in matches:
        try:
            tool_call = json.loads(match.strip())
            tool_calls.append(tool_call)
        except Exception as e:
            print(f"⚠️ Invalid tool block: {e}")
    return tool_calls


def main():
    print("📈 Finance AI Agent (Type 'exit' to quit)")
    print("-----------------------------------------")

    # Start MCP
    mcp_proc = start_mcp_server()
    if not mcp_proc:
        print("❌ Failed to start MCP server.")
        return

    history = [
        {
            "role": "system",
            "content": """You are a financial assistant. When necessary, you use tools via <tool>{...}</tool> format.
Here are the tools you can use:
- get_ticker_info
- get_ticker_news
- search_quote
- search_news
- get_top_etfs
- get_top_mutual_funds
- get_top_companies
- get_top_growth_companies
- get_top_performing_companies

You will use the <tool> JSON blocks to call these tools.
"""
        }
    ]

    try:
        while True:
            user_input = input("\n🧑 You: ").strip()
            if user_input.lower() in ("exit", "quit", "bye"):
                break

            history.append({"role": "user", "content": user_input})

            # Get response from OpenAI
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            response = client.chat.completions.create(
                model="gpt-4",
                messages=history,
                temperature=0.3
            )
            assistant_reply = response.choices[0].message.content
            print(f"\n🤖 Claude: {assistant_reply}")

            # Check if it includes <tool> blocks
            tool_calls = extract_tool_blocks(assistant_reply)

            if tool_calls:
                final_result = assistant_reply
                for tool in tool_calls:
                    method = tool.get("name")
                    params = tool.get("parameters", {})
                    print(f"🔧 Calling MCP tool: {method}({params})")
                    result = call_mcp(mcp_proc, method, params)

                    result_str = json.dumps(result.get("result", result.get("error", {})), indent=2)
                    final_result = final_result.replace(
                        f"<tool>{json.dumps(tool, indent=2)}</tool>",
                        f"<tool_result>\n{result_str}\n</tool_result>"
                    )

                # Now ask OpenAI to summarize the tool results for the user
                history.append({"role": "assistant", "content": final_result})
                history.append({"role": "system", "content": "Summarize the results in a helpful way. Do not show the raw JSON."})

                final_response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=history,
                    temperature=0.3
                )

                final_reply = final_response["choices"][0]["message"]["content"]
                print(f"\n📊 FinanceBot: {final_reply}")
                history.append({"role": "assistant", "content": final_reply})
            else:
                history.append({"role": "assistant", "content": assistant_reply})

    except KeyboardInterrupt:
        print("\n🛑 Stopping...")

    finally:
        if mcp_proc:
            mcp_proc.terminate()
            mcp_proc.wait()
            print("✅ MCP server terminated.")


if __name__ == "__main__":
    main()