from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from transformers import pipeline
import torch


app = FastAPI(title="AI Mini Chatbot - Optimized")


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str


class AIMiniChatBot:
    def __init__(self):
        self.memory: Dict[str, List[str]] = {}

        # Use GPU if available
        device = 0 if torch.cuda.is_available() else -1

        self.generator = pipeline("text-generation", model="distilgpt2", device=device)

    def build_prompt(self, user_id: str, message: str) -> str:
        history = self.memory.get(user_id, [])

        recent_history = history[-6:]

        prompt = "The following is a conversation with an AI assistant. The assistant is helpful and brief.\n\n"

        for _message in recent_history:
            prompt += _message + "\n"

        prompt = prompt + f"Human: {message}\nAI:"

        return prompt

    def get_reply(self, user_id: str, message: str) -> str:
        try:
            if user_id not in self.memory:
                self.memory[user_id] = []

            prompt = self.build_prompt(user_id, message)

            # Generate response
            result = self.generator(
                prompt,
                max_new_tokens=50,
                pad_token_id=50256,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.2,
                return_full_text=False,  # Only returns the AI's completion
            )

            print(f"Generation result: {result}")

            full_reply = result[0]["generated_text"].strip()

            clean_reply = full_reply.split("Human:")[0].split("\n")[0].strip()

            if not clean_reply:
                clean_reply = "I'm listening. Tell me more."

            self.memory[user_id].append(f"Human: {message}")
            self.memory[user_id].append(f"AI: {clean_reply}")

            return clean_reply

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return "I encountered an error while thinking. Please try again."


bot = AIMiniChatBot()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    reply = bot.get_reply(user_id=request.user_id, message=request.message)
    return ChatResponse(reply=reply)


@app.get("/")
async def root():
    return {
        "status": "AI Mini ChatBOT running",
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "model": "distilgpt2",
    }


@app.delete("/chat/{user_id}")
async def clear_memory(user_id: str):
    if user_id in bot.memory:
        del bot.memory[user_id]
        return {"message": f"Memory for {user_id} cleared"}
    return {"message": "User not found"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
