import subprocess
import time

def test_chatbot():
    process = subprocess.Popen(
        ["uv", "run", "python3", "-u", "tutorial/mcp_chatbot.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )

    try:
        # Wait for initialization
        time.sleep(5)
        
        # Send input
        print("Sending input: Add 5 and 10")
        process.stdin.write("Add 5 and 10\n")
        process.stdin.flush()
        
        time.sleep(5)
        
        # Send exit
        print("Sending input: exit")
        process.stdin.write("exit\n")
        process.stdin.flush()
        
        # Get output
        stdout, stderr = process.communicate(timeout=10)
        print("Chatbot Output:")
        print(stdout)
        print("Chatbot Errors:")
        print(stderr)
        
    except Exception as e:
        print(f"Error: {e}")
        process.kill()

if __name__ == "__main__":
    test_chatbot()
