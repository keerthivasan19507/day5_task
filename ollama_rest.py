import requests
import time

OLLAMA_URL = "http://localhost:11434"
MODEL = "study-assistant"


def run_non_streaming(prompt):
    start = time.perf_counter()
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": MODEL, "prompt": prompt, "stream": False},
        timeout=300,
    )
    response.raise_for_status()
    data = response.json()
    total = time.perf_counter() - start

    eval_count = data.get("eval_count", 0)
    eval_duration = data.get("eval_duration", 0) / 1_000_000_000
    tps = eval_count / eval_duration if eval_duration > 0 else 0

    print("\n=== NON-STREAMING /api/generate ===")
    print("Prompt:", prompt)
    print("Answer:", data.get("response", "").strip())
    print(f"Total time: {total:.3f} s")
    print(f"Tokens: {eval_count}")
    print(f"Tokens/sec: {tps:.2f}")


def run_streaming(prompt):
    start = time.perf_counter()
    ttft = None
    token_count = 0
    final_data = {}

    with requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": MODEL, "prompt": prompt, "stream": True},
        stream=True,
        timeout=300,
    ) as response:
        response.raise_for_status()
        print("\n=== STREAMING /api/generate ===")
        print("Prompt:", prompt)
        print("Answer: ", end="", flush=True)

        for line in response.iter_lines():
            if not line:
                continue

            data = line.decode("utf-8")
            import json
            item = json.loads(data)

            piece = item.get("response", "")
            if piece:
                if ttft is None:
                    ttft = time.perf_counter() - start
                token_count += 1
                print(piece, end="", flush=True)

            final_data = item

    total = time.perf_counter() - start
    eval_count = final_data.get("eval_count", token_count)
    eval_duration = final_data.get("eval_duration", 0) / 1_000_000_000
    tps = eval_count / eval_duration if eval_duration > 0 else 0

    print()
    print(f"TTFT: {ttft:.3f} s" if ttft is not None else "TTFT: not measured")
    print(f"Total time: {total:.3f} s")
    print(f"Tokens: {eval_count}")
    print(f"Tokens/sec: {tps:.2f}")


if __name__ == "__main__":
    prompt = "Explain binary search in simple language with a small example."
    run_non_streaming(prompt)
    run_streaming(prompt)
