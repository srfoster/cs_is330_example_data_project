from transformers import AutoTokenizer, AutoModelForCausalLM

# Read Hugging Face token from secure file
with open('hf_token.txt', 'r') as f:
    hf_token = f.read().strip()

tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it", token=hf_token)
model = AutoModelForCausalLM.from_pretrained("google/gemma-2-2b-it", token=hf_token)

input_text = "Write me a poem about Machine Learning."
input_ids = tokenizer(input_text, return_tensors="pt")

outputs = model.generate(**input_ids)
print(tokenizer.decode(outputs[0]))