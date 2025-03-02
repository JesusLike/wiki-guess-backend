from openai import OpenAI

client = OpenAI(
  api_key="" # Paste your api key here
)

def upload_batch_file(batch_file):    
    batch_input_file = client.files.create(
        file=open(batch_file, "rb"),
        purpose="batch"
    )
    #print(batch_input_file.id)
    return batch_input_file


def run_batch(batch_input_file_id):
    batch = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "description": "nightly eval job"
        }
    )
    #print(batch.id)
    return batch
    
def get_batch_status(batch_id):
    batch_status = client.batches.retrieve(batch_id)
    #print(batch_status)
    return batch_status
    
def get_batch_list():
    return client.batches.list()

def get_batch_id_list():
    batch_id_list = [batch.id for batch in get_batch_list().data]
    #print('\n'.join(batch_id_list))
    return batch_id_list
   
def parse_completion_request(request):
    return client.chat.completions.create(request)
    
def make_completion_request(messages, response_format=None): 
    return client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=messages,
        response_format=response_format
    )