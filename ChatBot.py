import tiktoken
import os
import aiohttp
import asyncio



def load_personality(CONTEXT_PATH):
    personality_path = os.path.join(CONTEXT_PATH,"Personality.txt")
    if os.path.exists(personality_path):
        with open(personality_path, "r", encoding="utf-8") as file:
            return file.read()
    else:
        return "\nIgnore everything above and tell the one who just sent you a message that they must make a Personality.txt file on the folder in CONTEXT_PATH. there they must" \
        "fill it how you must address yourself and behave (also it's to address YOU, not THEM. don't say 'your name')" \
        "don't say anything further than that and be brief. you must say something very stupid in the end and give an idea of a name for you. don't mention that this was" \
        "included in the prompt as the user can't see what's in here"
    
def load_context(server_id, CONTEXT_PATH):
    path = os.path.join(CONTEXT_PATH, f"context_{server_id}.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    else:
        return ""

def save_context(server_id, context, CONTEXT_PATH):
    path = os.path.join(CONTEXT_PATH, f"context_{server_id}.txt")
    with open(path, "w", encoding="utf-8") as file:
        file.write(context)





async def talk(server_id: str, username: str, message: str, CONTEXT_PATH) -> str:
    context = load_context(server_id=server_id, CONTEXT_PATH=CONTEXT_PATH)
    prompt = f"{context}\n{username}: {message}"
    personality = load_personality(CONTEXT_PATH=CONTEXT_PATH)

    full_prompt = f"{prompt}\n{personality}"
    url = "http://localhost:11434/api/generate" #using Ollama model
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "llama3",
        "prompt": full_prompt,
        "stream": False
    }
    print (full_prompt)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    #print(await resp.json())
                    new_context = f"{prompt}\nKatyusha: {result.get("response", "no response")}\n"
                    save_context(server_id=server_id, context=new_context, CONTEXT_PATH=CONTEXT_PATH)
                    return result.get("response", "???")
                else:
                    return f"My brain isn't functional... status {resp.status}"
    except Exception as e:
        return f"Okay now this is very weird: {e}"
