from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import requests
from requests.exceptions import RequestException
import urllib3


async def post_file_and_get_filename_fastapi(file: UploadFile, detect_url: str, get_image_url: str):
    try:
        files = {'file': (file.filename, file.file, 'image/jpeg')}
        headers = {'Accept': 'application/json'}

        response = requests.post(detect_url, files=files, headers=headers, verify=False)
        response.raise_for_status()  # Raise an exception for HTTP errors

        response_json = response.json()  # Convert response to JSON
        print("Response:")
        print(response_json)

        # Extract filename from response
        filename = response_json.get("filename")
        print(get_image_url + "/" + filename)
        if filename:
            print("Filename from response:", filename)
            # Assuming you have a get_image_from_filename function defined somewhere
            # get_image_from_filename(filename, get_image_url)
            return filename  # Return filename extracted from the response
        else:
            return "Filename not found in response."
    except FileNotFoundError as e:
        return f"File not found: {file.filename}"
    except RequestException as e:
        return f"Error: {e}"

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    return open("templates/index.html").read()


@app.post("/upload", response_class=HTMLResponse)
async def upload_file(file: UploadFile = File(...)):
    result_message = await post_file_and_get_filename_fastapi(file, detect_url, get_image_url)
    return open("templates/result.html").read().replace("{{ resultMessage }}", result_message)


detect_url = "https://model-yolo-ml-demo.apps.ocpbare.davenet.local/detect"
get_image_url = "https://model-yolo-ml-demo.apps.ocpbare.davenet.local/uploads/get/image"

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
