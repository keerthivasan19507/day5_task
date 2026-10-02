from openai import OpenAI

MODEL = "study-assistant"

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "system",
            "content": (
                "You are a strict computer science professor. "
                "Use technical terminology and give a precise explanation."
            ),
        },
        {
            "role": "user",
            "content": "Explain binary search.",
        },
    ],
)

print("=== OPENAI-COMPATIBLE API ===")
print("Program system prompt:")
print("You are a strict computer science professor.")
print("\nModel response:")
print(response.choices[0].message.content)
