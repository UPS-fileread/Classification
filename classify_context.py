#!/usr/bin/env python3
import argparse
import sys
import warnings
import os
from enum import Enum
from dotenv import load_dotenv
import json
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

# load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "defintions.json")
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    cfg = json.load(f)

CONTEXT_TYPES = cfg["context_types"]
SUBCATEGORIES  = cfg["subcategories"]
#SUBCATEGORY_DEFINITIONS  = cfg["subcategory_definitions"]

# model & categories
LANGUAGE_MODEL = 'gpt-4.1-2025-04-14'


class Category(Enum):
    Contract   = 'Contract'
    Litigation = 'Litigation'
    Regulatory = 'Regulatory'
    Financial  = 'Financial'
    Statutory  = 'Statutory'
    Email      = 'Email'
    other      = 'other'

class ClassificationResult(BaseModel):
    category: Category = Field(
        ...,
        description="One of the predefined legal-context categories",
        example="Regulatory"
    )
    subcategory: str = Field(
        ...,
        description="One of the predefined subcategories for the chosen category",
        example="Inspection Report"
    )

    class Config:
        use_enum_values = True
        validate_assignment = True

def classify_context(text: str) -> ClassificationResult:
    # build the prompt listing categories and their subcategories
    categories_fmt = '\n'.join(f" * {k}: {v}" for k, v in CONTEXT_TYPES.items())
    subcats_fmt = '\n'.join(
        f"   - {cat}:\n" +
        "\n".join(f"       • {sub}" for sub in SUBCATEGORIES.get(cat, []))
        for cat in CONTEXT_TYPES
    )
    system_prompt = f"""
You will be given a text block from a legal document.

First, choose the best fitting **category** from the list below,
using the description provided for each:

{categories_fmt}

Then, choose the best fitting **subcategory** from the list for that category:

{subcats_fmt}

Respond with a JSON object containing exactly two keys:
  {{ "category": "<Category>", "subcategory": "<Subcategory>" }}
where <Category> must be one of the keys above, and <Subcategory> must be one of the entries under that category.
"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": text},
    ]

    # make the API call to classify the text
    resp = client.responses.parse(
        model=LANGUAGE_MODEL,
        input=messages,
        text_format=ClassificationResult
    )

    # will either return a valid ClassificationResult or raise ValidationError
    return resp.output_parsed

def main():
    parser = argparse.ArgumentParser(
        description="Classify a TXT file into a legal context and subcategory."
    )
    parser.add_argument('txt_file', help="Path to the TXT file to classify")
    args = parser.parse_args()

    try:
        text = open(args.txt_file, 'r', encoding='utf-8').read()
    except Exception as e:
        print(f"Error reading '{args.txt_file}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = classify_context(text)
        print(f"Category   : {result.category}")
        print(f"Subcategory: {result.subcategory}")
    except ValidationError as e:
        warnings.warn(f"Failed to validate LLM response: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()