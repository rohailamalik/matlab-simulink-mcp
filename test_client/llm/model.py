import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()

api_base="https://aalto-openai-apigw.azure-api.net/v1"

openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("OpenAI API Key is not set. Please add it to the .env file.")

def create_azure_openai_model(model: str = "gpt-4o"):

    model_map = {
            "gpt-4o-mini": "gpt-4o-mini-2024-07-18",
            "gpt-4o": "gpt-4o-2024-11-20",
            "gpt-4.1-nano": "gpt-4.1-nano-2025-04-14",
            "gpt-4.1-mini": "gpt-4.1-mini-2025-04-14",
            "gpt-4.1": "gpt-4.1-2025-04-14",
            #"o1-mini": "o1-mini-2024-09-12",
            #"o1": "o1-2024-12-17",
            #"o3-mini": "o3-mini-2025-01-31"
        }

    if model not in model_map:
            raise ValueError(f"Unsupported model '{model}'. Currently available models: {list(model_map.keys())}")

    return AzureChatOpenAI(
         azure_deployment = model_map[model],
         api_version = "2025-03-01-preview",
         azure_endpoint = api_base,
         default_headers = {"Ocp-Apim-Subscription-Key": openai_api_key},
         )

model = create_azure_openai_model("gpt-4o-mini")