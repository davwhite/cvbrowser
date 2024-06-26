from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse
import requests
from requests.exceptions import RequestException
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# URLs
detect_url = os.environ.get("DETECT_URL")
get_image_url = os.environ.get("GET_IMAGE_URL")
get_images_url = os.environ.get("GET_IMAGES_URL")

# Directory for static files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

async def post_file_and_get_results(file: UploadFile):
    try:
        files = {'file': (file.filename, file.file, file.content_type)}
        response = requests.post(detect_url, files=files, verify=False)
        response.raise_for_status()
        return response.json(), file.filename
    except RequestException as e:
        return {"error": f"Error processing file: {e}"}, None

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Fetch list of images
    try:
        response = requests.get(get_images_url, verify=False)
        response.raise_for_status()
        data = response.json()
        images = data.get("images", [])
        # Generate links for images
        image_links = [f'<a href="{get_images_url}/image/{image}">{image}</a><br>' for image in images]
        image_links_str = "\n".join(image_links)
    except requests.RequestException as e:
        image_links_str = f"Error fetching images: {e}"

    content = f"""
        <html>
        <head>
            <title>Upload File</title>
            <link rel="stylesheet" type="text/css" href="/static/css/style.css">
        </head>
        <body>
            <div class="container">
                <h1>Upload File</h1>
                <form action="/upload" enctype="multipart/form-data" method="post">
                    <input type="file" name="file" accept=".jpeg,.jpg,.png">
                    <input type="submit" value="Upload File">
                </form>
                <h2>Images:</h2>
                {image_links_str}
            </div>
        </body>
        </html>
    """
    return HTMLResponse(content=content)

@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    results, filename = await post_file_and_get_results(file)
    if "error" in results:
        return HTMLResponse(content=f"<h2>Error: {results['error']}</h2>")
    
    detected_objects = results.get("detectedObj", [])
    content = f"""
        <html>
        <head>
            <title>Upload Result</title>
            <link rel="stylesheet" type="text/css" href="/static/css/style.css">
        </head>
        <body>
            <div class="container">
                <h1>Upload Result</h1>
                <h2>Filename: {filename}</h2>
                <h2>Detected Objects:</h2>
                <ul>
    """
    
    for obj in detected_objects:
        object_name = obj.get("object")
        object_count = obj.get("count")
        content += f"<li>{object_name}: {object_count}</li>"
    
    content += """
                </ul>
    """
    
    # If filename is available, display the resulting image
    if filename:
        image_content = f'<img src="{get_image_url}/{filename}" class="result-image" style="max-width: 800px;">'
        content += image_content
    
    content += """
            </div>
        </body>
        </html>
    """
    
    return HTMLResponse(content=content)

# Serve static files
@app.get("/static/{filepath:path}")
async def serve_static(filepath: str):
    return FileResponse(os.path.join(STATIC_DIR, filepath))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
