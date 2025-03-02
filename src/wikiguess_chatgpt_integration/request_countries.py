import json

from request_helper import load_countries, load_schema, get_country_request_content
from gpt_asker import make_completion_request

country_data = []
for country in load_countries():
    print(f"Retrieving data for {country}")
    messages = [
        {
            'role': 'user',
            'content': get_country_request_content(country)
        }
    ]
    response_format = {
        'type': 'json_schema',
        'json_schema': {
            'name': 'country_data',
            'strict': True,
            'schema': load_schema()
        }
    }
    completion = make_completion_request(messages, response_format=response_format)
    country_data.append(json.loads(completion.choices[0].message.content))
    print(completion.choices[0].message)
    print("\n")

with open('country_data.json', 'w', encoding='utf-8') as f:
    json.dump(country_data, f, ensure_ascii=False, indent=4)