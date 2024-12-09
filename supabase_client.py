import os
from supabase import create_client, Client

#print(os.environ)
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
POE_KEY: str = os.environ.get("POE_API_KEY")
supabase: Client = create_client(url, key)


def save_markdown_to_storage(bucket_name: str, file_name: str, file_path: str, content: str):
    # Save the content to a local file
    with open(file_name, 'w') as file:
        file.write(content)
        #print(f"\n{os.path.dirname(os.path.abspath(file))}\n")

    # with open(file_name, 'rb') as file:
    #     response= supabase.storage.from_(bucket_name).update(file=file, path=file_path, file_options={"cache-control": "3600", "upsert": "true"})

    with open(file_name, 'rb') as f:
        response = supabase.storage.from_(bucket_name).upload(file=f, path=file_path, file_options={"upsert": "true"})

    print(response)

    # Remove the local file after uploading
    os.remove(file_name)

    print("File uploaded successfully.")