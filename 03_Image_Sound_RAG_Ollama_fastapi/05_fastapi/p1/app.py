from fastapi import FastAPI
from typing import Union
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import asyncio
import httpx
import json

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

@app.get("/")
def read_root():
    '''
    This is the root endpoint of the API.
    It returns a simple dictionary with the key "Hello" and value "World".
    '''
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    '''
    This endpoint takes an item_id as a path parameter and an optional query parameter q.
    It returns a dictionary with the keys "item_id" and "q", where "item_id" is the value of the item_id path parameter,
    and "q" is the value of the query parameter q (or None if q is not provided).
    '''
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

async def fake_video_streamer(prompt):
    # Replace this URL with your Ngrok or other endpoint URL
    ollama_url = "http://localhost:11434"
    data = {
        "prompt": prompt,
        "model": 'tinyllama',
        "stream": True  # Enable streaming
    }

    async with httpx.AsyncClient() as client:
        try:
            async with client.stream("POST", f"{ollama_url}/api/generate", json=data) as response:
                if response.status_code == 200:
                    async for chunk in response.aiter_text():
                        try:
                            # Parse the chunk as JSON and yield only the 'response' value
                            json_chunk = json.loads(chunk)
                            if "response" in json_chunk:
                                yield json_chunk["response"]
                        except json.JSONDecodeError:
                            yield "Error: Unable to parse chunk as JSON."
                else:
                    yield f"Error: {response.status_code}, {response.text}"
        except httpx.RequestError as exc:
            yield f"An error occurred while requesting data: {str(exc)}"

@app.get("/llm")
async def llm(prompt: str):
    '''
    This endpoint takes a prompt as a query parameter and returns a streaming response
    of textual chunks.
    '''
    await asyncio.sleep(1)
    return StreamingResponse(fake_video_streamer(prompt), media_type="text/plain")

# uvicorn main:app --reload
