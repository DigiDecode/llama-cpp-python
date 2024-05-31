from fastapi import Request
from fastapi.responses import JSONResponse
from llama_cpp.server.settings import ServerSettings, ModelSettings
from llama_cpp.server.app import create_app
import uvicorn
import llama_cpp
import asyncio

def dprint(*args, **kwargs):
    print(*args, **kwargs)

model_path = '/home/zbuntu/projects/Codestral-22B-v0.1-Q5_K_M.gguf'

server_settings = ServerSettings()
server_settings.host = "127.0.0.1"
server_settings.port = 4321

model_setting: dict = {
    "model": model_path,
    "model_alias": "codegemma-7b8bit",
    "n_gpu_layers": -1,
    "rope_scaling_type": llama_cpp.LLAMA_ROPE_SCALING_TYPE_LINEAR,
    "rope_freq_base": 1000000.0,
    "rope_freq_scale": 1,
    "n_ctx": 16000,
    "n_threads":1
}

app = create_app(
    server_settings=server_settings,
    model_settings=[ModelSettings(**model_setting)],
)
 
lock = asyncio.Lock()
queue = asyncio.Queue(maxsize=1)  # Set the queue size to 1

async def wait_for_disconnect(request: Request, queue):
    dprint('starting to wait for disconnect')
    while True:
        if await request.is_disconnected():
            break
        await asyncio.sleep(0.5)
    dprint('client disconnected')
    await queue.get()
    dprint('request removed from queue')


@app.middleware("http")
async def synchronize_requests(request: Request, call_next):
    try:
        dprint('adding request to queue')
        await queue.put(request)  # Add the request to the queue

        dprint('request added to queue')
        async with lock:
            dprint('acquired lock serving request')
            try: 
                # Process the request
                response = await call_next(request)
                dprint('response received')
                asyncio.create_task(wait_for_disconnect(request, queue))
                dprint('wait for disconnect thread created')
                # print(response)
                return response
            finally:
                dprint('request processed')
    except asyncio.QueueFull:
        dprint('exceptoin encountered')
        # If the queue is full, return a 503 error response
        return JSONResponse(status_code=503, content={"error": "Service unavailable, try again later"})


uvicorn.run(
    app,
    host=server_settings.host,
    port=server_settings.port,
    ssl_keyfile=server_settings.ssl_keyfile,
    ssl_certfile=server_settings.ssl_certfile,
)
