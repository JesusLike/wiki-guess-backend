import sys
import json
import jsonlines

def load_schema():
    with open('country_schema.json', 'r') as f:
        schema = json.load(f)
    return schema

def load_countries():
    with open('countries.txt', 'r') as f:
        #countries = f.readlines()
        return [country.rstrip() for country in f]

def get_country_request_content(country):
    return (f"Here's the list of questions and exemplary answers to each of them. Give me the answers to these questions about {country}:\n"
    "1) Name of the country. Example: \"Canada\".\n"
    "2) Name of the capital city de jure (put \"None\" if there are no capital). Example: \"Ottawa\".\n"
    "3) The area of the country in square kilometers (include units of measure in the answer). Example: \"9984670 sq. km\".\n"
    "4) Country's rank in the world by it's area. Example: 2.\n"
    "5) Country's nominal GDP in USD (include units of measure in the answer). Example: \"2.14 trillion USD\".\n"
    "6) Country's rank in the world by it's total nominal GDP. Example: 9.\n"
    "7) Country's nominal GDP per capita in USD (include units of measure in the answer). Example: \"53371 USD\".\n"
    "8) Country's rank in the world by it's nominal GDP per capita. Example: 20.\n"
    "9) Country's population amount (include units of measure in the answer). Example: \"41465298 people\".\n"
    "10) Country's rank in the world by population. Example: 37.\n"
    "11) Country's population density in people by square kilometer (include units of measure in the answer). Example: \"4.35 people per sq. km\".\n"
    "12) Country's rank in the world by it's population density. Example: 186.\n"
    "13) Year of establishment or independence (the most recent if there were few). Example: 1867.\n"
    "14) Previous colonial power or powers if there were any (put \"None\" otherwise). Example: \"United Kingdom\".\n"
    "15) Country's government type. Example: \"Parliamentary Democracy\".\n"
    "16) Country's official religion (put \"None\" if there are no official religion). Example: \"None\".\n"
    "17) Country's official currency code. Example: \"CAD\".\n"
    "18) Country's official language or languages. Example: \"English\", \"French\".\n"
    )

def generate_request(id, content, response_format=None):
    return {
        "custom_id": str(id), 
        "method": "POST", 
        "url": "/v1/chat/completions", 
        "body": {
            "model": "gpt-4o-mini", 
            "messages": [
                {
                    "role": "user", 
                    "content": content
                }
            ],
            "response_format": response_format
        }
    }

def generate_country_request(id, country, schema):
    response_format = { 
                "type": "json_schema", 
                "json_schema": {
                    "name": "country_data",
                    "strict": True, 
                    "schema": schema
                } 
            }
    return generate_request(id, get_country_request_content(country), response_format)

def generate_countries_batch_request(countries, schema):
    batch_request = []
    for index, country in enumerate(countries):        
        batch_request.append(generate_country_request(index + 1, country, schema))
    return batch_request
        
def create_sample_batch_file():
    schema = load_schema()
    with jsonlines.open('sample_request.jsonl', mode='w') as f:
        f.write_all([
                generate_country_request(1, "Canada", schema), 
                generate_country_request(2, "Afghanistan", schema),
                generate_country_request(3, "North Korea", schema)
            ])
        
def create_countries_batch_file():
    batch_request = generate_countries_batch_request(load_countries(), load_schema())
    with jsonlines.open('countries_batch_file.jsonl', mode='w') as f:
        f.write_all(batch_request)
        
# if __name__ == '__main__':
#     globals()[sys.argv[1]]()