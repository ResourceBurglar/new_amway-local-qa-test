# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import openai

openai.api_base = "http://10.143.33.252:19327/v1"

# Enter any non-empty API key to pass the client library's check.
openai.api_key = "chinese-llama-alpaca-2"

# Enter any non-empty model name to pass the client library's check.
completion = openai.ChatCompletion.create(
    model="chinese-llama-alpaca-2",
    messages=[
        {"role": "user", "content": 'hello!'},
    ],
    stream=False,
    temperature=0.4,
    max_new_tokens=4096,
)

print(completion)
