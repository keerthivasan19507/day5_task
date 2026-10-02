# Day 5 - Serving Models Your Way

## 1. Scenario

For this task, I chose a **College Study Assistant** scenario. The custom model is designed to answer college-study questions in simple, beginner-friendly language, keep answers short and clear, and use a simple example when useful.

The base model used is `qwen2.5:1.5b`, which was already available locally through Ollama. The custom model is named `study-assistant`.

## 2. What is Ollama?

Ollama is a local model-serving system that lets a model run on a local computer and be accessed through different interfaces. In this project, the model can be used from the Ollama command line, the Ollama REST API, and the OpenAI-compatible API.

For this scenario, a request can be sent to the local Ollama server. Ollama receives the request, loads or reuses the model, runs inference, and returns the generated answer. The exact local model storage location is machine-dependent, so it should be verified on the computer used for the experiment rather than guessed.

### Three parts of the Ollama setup

1. **Ollama CLI** - used for commands such as `ollama list`, `ollama show`, `ollama run`, `ollama create`, and `ollama ps`.
2. **Ollama server** - receives requests and manages model execution.
3. **Model files / model storage** - contains the local model data used by the server.

## 3. What is a Modelfile?

A Modelfile describes how to create a customized model from an existing base model.

This project uses:

- `FROM qwen2.5:1.5b` to select the base model.
- `PARAMETER temperature 0.3` to make responses more controlled and less random.
- `PARAMETER num_ctx 2048` to set the context window used for this custom model.
- `SYSTEM` to define the default behaviour of the College Study Assistant.

The custom model does not represent a second downloaded copy of the base model in the sense of downloading a new model from the internet. It packages configuration and behaviour around the selected base model.

## 4. System Prompt Priority

The Modelfile gives the model a default system instruction:

> "You are a college study assistant. Explain concepts in simple beginner-friendly language."

The Python program can provide its own system message when making a request.

In this experiment, the OpenAI-compatible Python script supplied a different system instruction:

> "You are a strict computer science professor. Use technical terminology and give a precise explanation."

The resulting response was more technical and detailed than the earlier response from the College Study Assistant. It explained binary search using technical terms such as initialization, bisection, recursive search, edge cases, and time complexity.

Therefore, the experiment showed that the **program-provided system instruction affected the response and changed the model's behaviour from the default style defined in the Modelfile**.

For an agent application, this is useful because the application can provide task-specific instructions at request time while still having a reusable default configuration in the Modelfile.


## 5. REST API

### `/api/generate`

`/api/generate` is suitable for a direct prompt-and-response generation request. In this project, it is used for both a normal non-streaming request and a streaming request.

### `/api/chat`

`/api/chat` is designed for chat-style messages containing roles such as system, user, and assistant. It is useful when the application needs conversational message history.

### OpenAI-compatible endpoint

Ollama also exposes an OpenAI-compatible interface. This matters because code written against an OpenAI-style client can be adapted to another compatible model server with fewer application-level changes.

## 6. Streaming and Performance

**Streaming** means the server sends generated output progressively instead of waiting for the complete response.

**TTFT (Time To First Token)** measures how long it takes before the first generated output becomes available.

**Total time** measures the complete duration of the request.

Streaming can make an answer feel faster because the user sees the beginning of the response earlier. It does not necessarily reduce the total amount of computation required to generate the complete answer.

In my experiment, the non-streaming request took **25.086 seconds**, generated **412 tokens**, and achieved **17.97 tokens/sec**.

The streaming request had a **TTFT of 2.116 seconds**, a **total time of 20.359 seconds**, generated **313 tokens**, and achieved **17.16 tokens/sec**.

The two tests generated different numbers of tokens, so their total times should not be treated as a direct apples-to-apples speed comparison. The streaming test demonstrates that output started arriving after about 2.116 seconds.

| Test          |         TTFT | Total time | Tokens | Tokens/sec |
| ------------- | -----------: | ---------: | -----: | ---------: |
| Non-streaming | Not measured |   25.086 s |    412 |      17.97 |
| Streaming     |      2.116 s |   20.359 s |    313 |      17.16 |




## 7. Context and Memory

`num_ctx` controls the context size used by the model. A larger context can require more memory because the model needs to maintain more information for inference.

`OLLAMA_KEEP_ALIVE` controls how long a model remains loaded in memory after a request.

`OLLAMA_NUM_PARALLEL` controls how many parallel requests can be processed for a model.

The KV cache stores intermediate attention information for tokens already processed. Increasing the context length can therefore increase KV-cache memory requirements.

## 8. KV Cache, PagedAttention and Prefix Caching

A simple serving system can reserve or manage KV-cache memory inefficiently when many requests have different sequence lengths. This can result in unused memory and fragmentation.

PagedAttention addresses this problem by organizing KV-cache data into fixed-size blocks and using a block table to map logical sequences to those blocks.

Prefix caching can reuse cached computation for a shared prompt prefix. For an agent, this can be useful when the same system prompt or other long prefix is repeatedly sent with different user requests.

## 9. Static Batching and Continuous Batching

Static batching groups requests together before processing. The group is relatively fixed.

Continuous batching allows new requests to join scheduling as other requests finish or progress. This is useful for serving many users because the server can keep the hardware busy.

Important measurements include:

- **Throughput** - how much work the server completes over time.
- **TTFT** - time until the first generated token.
- **TPOT (Time Per Output Token)** - time spent per generated output token.
- **P95 latency** - the latency below which 95% of requests finish.

Increasing throughput can increase queueing or latency, so serving systems balance throughput and responsiveness rather than maximizing only one measurement.

## 10. Ollama vs vLLM

| Basis | Ollama | vLLM |
|---|---|---|
| Built for | Simple local model serving and development | High-throughput model serving |
| Hardware | Suitable for a local machine with enough CPU/GPU/RAM | Usually deployed on server-grade GPU infrastructure |
| Several requests at once | Provides local serving and parallel-request controls | Designed for efficient concurrent serving |
| Memory management | Standard local model/KV-cache management | Uses techniques such as PagedAttention |
| Setup effort and model format | Simple setup with Ollama and Modelfiles | More production-oriented serving setup |
| My choice if only I use the scenario | Ollama - simple local setup is sufficient | — |
| My choice if 100 people use it at once | — | vLLM - designed for high-concurrency serving |

## 11. Minimal Implementation

The repository contains:

- `Modelfile`
- `ollama_rest.py`
- `openai_compatible.py`
- `analysis.md`
- `requirements.txt`
- `screenshots/`

The REST script sends both non-streaming and streaming requests to `/api/generate`.

The OpenAI-compatible script sends a different system prompt so that the behaviour can be observed experimentally.

| Prompt                                   | Followed Modelfile behaviour?               |     TTFT | Total time | Tokens/sec | Already loaded? |
| ---------------------------------------- | ------------------------------------------- | -------: | ---------: | ---------: | --------------- |
| Explain binary search in simple terms.   | Yes, generally simple and beginner-friendly | 2.116 s* |  20.359 s* |     17.16* | Yes             |
| What is a stack in data structures?      | Not recorded                                |        — |          — |          — | Yes             |
| Explain recursion with a simple example. | Not recorded                                |        — |          — |          — | Yes             |

* These measurements are from the streaming REST API test using the binary-search prompt. They should not be interpreted as measurements for the other prompts.


## 13. Suitability

For one person using a small study-assistant scenario on a local machine, Ollama is sufficient because the setup is simple and the model can be served locally.

For a shared deployment with many simultaneous users, a serving system designed for high concurrency such as vLLM becomes relevant because memory management, scheduling, batching, throughput, and latency become much more important.

## 14. Conclusion

This experiment demonstrates how Ollama can serve a locally available model through multiple interfaces. A Modelfile provides reusable default behaviour and parameters, while the REST API lets a Python program interact with the model directly. The OpenAI-compatible endpoint provides another application interface that can make migration between compatible serving systems easier.

The main difference between a simple local setup and a large shared deployment is the serving problem created by concurrency. When many requests arrive together, KV-cache memory, scheduling, batching, throughput, TTFT, TPOT, and P95 latency become important. Techniques such as PagedAttention and continuous batching are intended to address these production-serving challenges.
