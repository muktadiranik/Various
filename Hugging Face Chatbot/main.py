from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from transformers import pipeline
import torch

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(title="AI Mini Chatbot - Optimized")

# -----------------------------
# Request / Response Models
# -----------------------------


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str

# -----------------------------
# AI Chatbot Engine
# -----------------------------


class AIMiniChatBot:
    def __init__(self):
        self.memory: Dict[str, List[str]] = {}

        device = 0 if torch.cuda.is_available() else -1
        print(f"Loading model on {'GPU' if device == 0 else 'CPU'}...")

        self.generator = pipeline(
            "text-generation",
            model="distilgpt2",
            device=device
        )

    def build_prompt(self, user_id: str, message: str) -> str:
        """Combine conversation history into a prompt with a clean format"""
        history = self.memory.get(user_id, [])
        # Only take the last 3 exchanges (6 lines) to stay within GPT-2's context window
        recent_history = history[-6:]

        prompt = "The following is a conversation with an AI assistant. The assistant is helpful and brief.\n\n"
        for msg in recent_history:
            prompt += msg + "\n"

        prompt += f"Human: {message}\nAI:"
        return prompt

    def get_reply(self, user_id: str, message: str) -> str:
        try:
            if user_id not in self.memory:
                self.memory[user_id] = []

            prompt = self.build_prompt(user_id, message)

            # Generate response
            # Note: return_full_text=False makes extraction much easier
            result = self.generator(
                prompt,
                max_new_tokens=50,
                pad_token_id=50256,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.2,
                return_full_text=False  # Only returns the AI's completion
            )
            print(f"Generation result: {result}")

            full_reply = result[0]["generated_text"].strip()

            # Fix: DistilGPT2 often starts writing the Human's next line.
            # We cut the response at the first newline or "Human:" mention.
            clean_reply = full_reply.split("Human:")[0].split("\n")[0].strip()

            if not clean_reply:
                clean_reply = "I'm listening. Tell me more."

            # Save to memory for context
            self.memory[user_id].append(f"Human: {message}")
            self.memory[user_id].append(f"AI: {clean_reply}")

            return clean_reply

        except Exception as e:
            print(f"Error generating response: {e}")
            return "I encountered an error while thinking. Please try again."


# Initialize bot as a singleton
bot = AIMiniChatBot()

# -----------------------------
# API Endpoints
# -----------------------------


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    reply = bot.get_reply(user_id=request.user_id, message=request.message)
    return ChatResponse(reply=reply)


@app.get("/")
async def root():
    return {
        "status": "AI Mini Chatbot running",
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "model": "distilgpt2"
    }


@app.delete("/chat/{user_id}")
async def clear_memory(user_id: str):
    """Endpoint to reset a conversation"""
    if user_id in bot.memory:
        del bot.memory[user_id]
        return {"message": f"Memory for {user_id} cleared."}
    return {"message": "User not found."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
