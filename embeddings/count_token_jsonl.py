import tiktoken
import json

# Initialize the tokenizer for the "text-embedding-ada-002" model
tokenizer = tiktoken.encoding_for_model("text-embedding-ada-002")

# Function to count tokens for each input text
def count_tokens(text):
    return len(tokenizer.encode(text))

# Open the JSONL file and check token counts
jsonl_file_path = 'batch_input.jsonl'

# Reading the file
with open(jsonl_file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

token_counts = []

for line in lines:
    data = json.loads(line)
    input_text = data['body']['input']
    token_count = count_tokens(input_text)
    token_counts.append({"custom_id": data['custom_id'], "tokens": token_count})

# Sort by token count and print the top 5 inputs with the highest token counts
sorted_token_counts = sorted(token_counts, key=lambda x: x["tokens"], reverse=True)
for entry in sorted_token_counts[:5]:
    print(f"Custom ID: {entry['custom_id']}, Tokens: {entry['tokens']}")
