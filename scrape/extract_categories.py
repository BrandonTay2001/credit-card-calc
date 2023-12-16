from openai import OpenAI
import json

MODEL = "gpt-4-1106-preview"

tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_categories",
            "description": "extract the individual categories from the text, categories can be one of the following: Groceries, Petrol, Dining, Online Shopping, Others",
            "parameters": {
                "type": "object",
                "properties": {
                    "categories": {
                        "type": "string",
                        "description": "categories in the text, separated by commas"
                    }
                },
                "required": ["categories"]
            }
        }
    }
]

client = OpenAI(api_key="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")

messages = [{"role": "system", "content": "extract categories from text. remember that 'Others' refers to local retail spending other than utilities, overseas spending, insurance, travel, and government-related transactions"}, 
            {"role": "user", "content": "selected groceries, utilities plus petrol spending"}]
chat = client.chat.completions.create(
    model = MODEL,
    messages=messages,
    tools=tools,
    tool_choice={"type": "function", "function": {"name": "extract_categories"}}
)
categories = chat.choices[0].message.tool_calls[0].function.arguments
# convert to json
categories = json.loads(categories)
# convert comma separated value to array of strings
categories = categories["categories"].split(", ")
print(categories)