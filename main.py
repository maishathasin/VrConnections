from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

client = OpenAI(api_key="")

app = FastAPI()

class ChatInput(BaseModel):
    message: str

@app.post("/chat")
async def chat_with_gpt(input_data: ChatInput):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Your system message, if any"},
                {"role": "user", "content": input_data.message}
            ]
        )
        chat_response = response.choices[0].message.content
        return {"response": chat_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)