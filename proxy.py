import time
import json
import asyncio
import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

# Set up logging configuration (log to both console and a proxy.log file)
log_file_path = os.path.join(os.path.dirname(__file__), "proxy.log")
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] (%(name)s) %(message)s",
    handlers=[
        logging.FileHandler(log_file_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AntigravityProxy")

app = FastAPI(title="Antigravity OpenAI Proxy via CLI")

@app.on_event("startup")
async def startup_event():
    logger.info("Antigravity CLI-based OpenAI Proxy started. Subprocess bridging enabled.")
    logger.info(f"Logging active. Writing logs to: {log_file_path}")

@app.get("/v1/models")
async def get_models():
    logger.info("Received GET /v1/models request")
    return {
        "object": "list",
        "data": [
            {"id": "agy-agent", "object": "model", "created": int(time.time()), "owned_by": "google"},
            {"id": "gemini-2.0-flash", "object": "model", "created": int(time.time()), "owned_by": "google"},
            {"id": "gemini-2.0-pro-exp", "object": "model", "created": int(time.time()), "owned_by": "google"},
            {"id": "gemini-1.5-pro", "object": "model", "created": int(time.time()), "owned_by": "google"},
            {"id": "gemini-1.5-flash", "object": "model", "created": int(time.time()), "owned_by": "google"}
        ]
    }

async def run_agy_cli(prompt: str) -> str:
    logger.info(f"Spawning agy CLI subprocess for prompt: {prompt[:100]}...")
    try:
        proc = await asyncio.create_subprocess_exec(
            "/Users/songmyeongjin/.local/bin/agy",
            "-p", prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            result = stdout.decode("utf-8").strip()
            logger.info(f"agy CLI execution successful. Output length: {len(result)} characters.")
            return result
        else:
            err_msg = stderr.decode("utf-8").strip()
            logger.error(f"agy CLI exited with code {proc.returncode}. Error: {err_msg}")
            return f"Error from agy CLI: {err_msg}"
    except Exception as e:
        logger.exception("Failed to run agy CLI subprocess due to exception")
        return f"Proxy Subprocess Error: {str(e)}"

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    stream = data.get("stream", False)
    
    if not messages:
        logger.warning("Empty messages list received in chat completions request")
        return {"error": "No messages provided."}
        
    last_message = messages[-1].get("content", "")
    logger.info(f"Chat completions request received. Stream={stream}, Prompt length={len(last_message)} chars")
    
    # Run the subprocess to get the response text
    response_text = await run_agy_cli(last_message)
    logger.info(f"Returning response content (truncated): {response_text[:100]}...")

    if stream:
        async def generate():
            chunk_size = 5
            for i in range(0, len(response_text), chunk_size):
                token = response_text[i:i+chunk_size]
                chunk = {
                    "id": f"chatcmpl-agy-{int(time.time())}",
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": "agy-agent",
                    "choices": [{"delta": {"content": token}, "index": 0, "finish_reason": None}]
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.01)
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        return {
            "id": f"chatcmpl-agy-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "agy-agent",
            "choices": [{
                "message": {"role": "assistant", "content": response_text},
                "index": 0,
                "finish_reason": "stop"
            }]
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
