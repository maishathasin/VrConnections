from fastapi import FastAPI, HTTPException,Request
from pydantic import BaseModel
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import os
from jinja2 import Environment, FileSystemLoader







# Initialize Jinja2Templates with the directory containing your templates
templates = Jinja2Templates(directory="examples")


env = Environment(loader=FileSystemLoader('examples'))


client = OpenAI(api_key="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")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Pydantic models for request and response data
class ChatInput(BaseModel):
    message: str

class EnvironmentConfig(BaseModel):
    configuration: str

# Endpoint for handling chat with GPT
@app.post("/chat")
async def chat_with_gpt(request: Request, input_data: ChatInput):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """ You are an experienced webVR developer using a-frame. Please assist me in creating a scene according what the user needs. You have access to many assets, in the asset folder that you can use these are: ../examples/assets/bench.glb , ../examples/assets/Cedrus-Libani-tree.glb,  ../examples/assets/flower.glb,  ../examples/assets/grass-field.glb,   ../examples/assets/Slides.glb,  ../examples/assets/Swings.glb. You are to create using these assets and the environment component in a-frame to create a scene. First lets start with assets . Think about what the scene looks like step by step, including what the positioning is like, with the position being x,y,z
You are to return a JSON with the key being the asset name, and the value being a list of lists with all the positions you’d like the the asset to be in the scene.  The scene is extremely large with more than 200 x 200, so make sure there are small items. 
                 Do not return back a lot of models as web browser is slow. The grass-field is very big and the perfect y position for this is -40, otherwise its floating. 
                 Donot return too many grass fields as they are massive. If User is asking for town/city like features use only this asset instead https://cdn.glitch.global/3536bdd6-2ff7-42ca-b434-8724824d9838/Tree%20oak%201%20N070221.mtl?v=1705172731901

Here are some examples for you:

Input: Create me a scene of a forest
Output: {“assets/tree.gtlf”: [
    [0, 0, 0], [2, 0, 2], [4, 0, 4], [6, 0, 6], [8, 0, 8], // trees
    [10, 0, 10], [12, 0, 12], [14, 0, 14], [16, 0, 16], [18, 0, 18],
    [20, 0, 20], [22, 0, 22], [24, 0, 24], [26, 0, 26], [28, 0, 28],
    [110, 0, 110], [112, 0, 112], [114, 0, 114], [116, 0, 116], [118, 0, 118],
    [120, 0, 120], [122, 0, 122], [124, 0, 124], [126, 0, 126], [128, 0, 128],
    [130, 0, 130], [132, 0, 132], [134, 0, 134], [136, 0, 136], [138, 0, 138],
    [140, 0, 140], [142, 0, 142], [144, 0, 144], [146, 0, 146], [148, 0, 148],
“assets/flower.gtlf”: [    [3, 0, 5], [7, 0, 10], [12, 0, 15], [17, 0, 20], [22, 0, 25], 
    [27, 0, 30], [32, 0, 35], [37, 0, 40], [42, 0, 45], [47, 0, 50]],
 “assets/animals.gtlf”: [
    [5, 0, 8], [15, 0, 18], [25, 0, 28], [35, 0, 38], [45, 0, 48] 
  ],
}

With these as references , JUST GIVE ME THE JSON WITHOUT ANY TEXT BEFORE OR AFTER, this is VERY important """},
                {"role": "user", "content": input_data.message}
            ]
        )
        print(response)
        chat_response = response.choices[0].message.content
        print(chat_response)
        environment_data = process_gpt_response(chat_response)  # Convert GPT response to a suitable format
        return templates.TemplateResponse("basic-chat.html", {
                    "request": request,  # Pass the actual request object
                    "environment_data": environment_data
                })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
           
    


# Endpoint for creating the environment
@app.post("/environment")
async def create_environment(request: Request, input_data: ChatInput):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": '''You are an experienced webVR developer using a-frame. Please assist me in creating a scene according what the user needs.Now we are going to create the environment , Using the following parameters, please create an environment configuration string.  Based on the input, you should return a configuration string like environment = "preset: forest; groundColor: #445; grid: cross". Here are the available parameters and their default values:

* 		preset: Choose from 'none', 'default', 'contact', 'egypt', 'checkerboard', 'forest', 'goaland', 'yavapai', 'goldmine', 'threetowers', 'poison', 'arches', 'tron', 'japan', 'dream', 'volcano', 'starry', 'osiris', 'moon'.
* 		seed: Any integer - Seed for randomization.
* 		skyType: Choose from 'color', 'gradient', 'atmosphere'.
* 		skyColor: Any color value (e.g., '#FFFFFF') - Main sky color.
* 		horizonColor: Any color value - Color of the sky near the horizon.
* 		lighting: Choose from 'none', 'distant', 'point'.
* 		shadow: true or false - Toggles shadows.
* 		shadowSize: Any integer - Size of shadows.
* 		lightPosition: Coordinate values in the format 'x y z'.
* 		fog: A number between 0 and 1 - Amount of fog.
* 		ground: Choose from 'none', 'flat', 'hills', 'canyon', 'spikes', 'noise'.
* 		groundTexture: Choose from 'none', 'checkerboard', 'squares', 'walkernoise'.
* 		groundColor: Any color value - Main color of the ground.
* 		groundColor2: Any color value - Secondary color of the ground.
* 		dressing: Choose from 'none', 'cubes', 'pyramids', 'cylinders', 'towers', 'mushrooms', 'trees', 'apparatus', 'torii'.

* 		grid: Choose from 'none', '1x1', '2x2', 'crosses', 'dots', 'xlines', 'ylines'.
* 		gridColor: Any color value - Color of the grid.


Think very carefully on what the environment of the {input} looks like, and then return the string in this format environment = "preset: forest; groundColor: #445; grid: cross" . THIS IS FORMAT IS VERY IMPORTANT ONLY RETURN IN THIS FORMAT. AND JUST GIVE ME THE OUTPUT WITHOUT ANY TEXT BEFORE OR AFTER THIS IS VERY IMPORTANT '''},
                {"role": "user", "content": input_data.message}
            ]
        )
      

        full_response = response.choices[0].message.content.strip()
        # Extract the configuration part from the response
        config_start = full_response.find('"') + 1
        config_end = full_response.rfind('"')
        environment_config = full_response[config_start:config_end]


        # Prepare the response data
        env_config = EnvironmentConfig(configuration=environment_config)

        
        # Return response using Jinja2 template
        return templates.TemplateResponse("basic-chat.html", {
            "request": request,
            "environment_config": env_config,
            "environment_data": {}
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Endpoint for creating the environment
@app.post("/scene")
async def create_environment(request: Request, input_data: ChatInput):
    response = client.chat.completions.create(
    model="gpt-4",
    messages=[
                {"role": "system", "content": """ You are an experienced webVR developer using a-frame. Please assist me in creating a scene according what the user needs. You have access to many assets, in the asset folder that you can use these are: assets/bench.glb , assets/Cedrus-Libani-tree.glb, assets/flower.glb,  assets/grass-field.glb,  assets/Slides.glb,  assets/Swings.glb. You are to create using these assets and the environment component in a-frame to create a scene. First lets start with assets . Think about what the scene looks like step by step, including what the positioning is like, with the position being x,y,z
You are to return a JSON with the key being the asset name, and the value being a list of lists with all the positions you’d like the the asset to be in the scene.  
                 Do not return back a lot of models as web browser is slow. The grass-field is very big and the perfect y position for this is -40, otherwise its floating. 
                 Donot return too many grass fields as they are massive. If User is asking for town/city like features use only this asset instead https://cdn.aframe.io/test-models/models/glTF-2.0/virtualcity/VC.gltf

Here are some examples for you:

Input: Create me a scene of a forest
Output: {“assets/tree.gtlf”: [
    [0, 0, 0], [2, 0, 2], [4, 0, 4], [6, 0, 6], [8, 0, 8], // trees
    [10, 0, 10], [12, 0, 12], [14, 0, 14], [16, 0, 16], [18, 0, 18],
    [20, 0, 20], [22, 0, 22], [24, 0, 24], [26, 0, 26], [28, 0, 28],
    [110, 0, 110], [112, 0, 112], [114, 0, 114], [116, 0, 116], [118, 0, 118],
    [120, 0, 120], [122, 0, 122], [124, 0, 124], [126, 0, 126], [128, 0, 128],
    [130, 0, 130], [132, 0, 132], [134, 0, 134], [136, 0, 136], [138, 0, 138],
    [140, 0, 140], [142, 0, 142], [144, 0, 144], [146, 0, 146], [148, 0, 148],
“assets/flower.gtlf”: [    [3, 0, 5], [7, 0, 10], [12, 0, 15], [17, 0, 20], [22, 0, 25], 
    [27, 0, 30], [32, 0, 35], [37, 0, 40], [42, 0, 45], [47, 0, 50]],
 “assets/animals.gtlf”: [
    [5, 0, 8], [15, 0, 18], [25, 0, 28], [35, 0, 38], [45, 0, 48] 
  ],
}

With these as references , JUST GIVE ME THE JSON WITHOUT ANY TEXT BEFORE OR AFTER, this is VERY important  """},
                {"role": "user", "content": input_data.message}
            ]
        )
    print(response)
    chat_response = response.choices[0].message.content
    print(chat_response)
    environment_data = process_gpt_response(chat_response)  # Convert GPT response to a suitable format

# prompt 2 
    response = client.chat.completions.create(
    model="gpt-4",
    messages=[
                {"role": "system", "content": '''You are an experienced webVR developer using a-frame. Please assist me in creating a scene according what the user needs.Now we are going to create the environment , Using the following parameters, please create an environment configuration string.  Based on the input, you should return a configuration string like environment = "preset: forest; groundColor: #445; grid: cross". Here are the available parameters and their default values:

* 		preset: Choose from 'none', 'default', 'contact', 'egypt', 'checkerboard', 'forest', 'goaland', 'yavapai', 'goldmine', 'threetowers', 'poison', 'arches', 'tron', 'japan', 'dream', 'volcano', 'starry', 'osiris', 'moon'.
* 		seed: Any integer - Seed for randomization.
* 		skyType: Choose from 'color', 'gradient', 'atmosphere'.
* 		skyColor: Any color value (e.g., '#FFFFFF') - Main sky color.
* 		horizonColor: Any color value - Color of the sky near the horizon.
* 		lighting: Choose from 'none', 'distant', 'point'.
* 		shadow: true or false - Toggles shadows.
* 		shadowSize: Any integer - Size of shadows.
* 		lightPosition: Coordinate values in the format 'x y z'.
* 		fog: A number between 0 and 1 - Amount of fog.
* 		ground: Choose from 'none', 'flat', 'hills', 'canyon', 'spikes', 'noise'.
* 		groundYScale: Any integer - Maximum height of ground features.
* 		groundTexture: Choose from 'none', 'checkerboard', 'squares', 'walkernoise'.
* 		groundColor: Any color value - Main color of the ground.
* 		groundColor2: Any color value - Secondary color of the ground.
* 		dressing: Choose from 'none', 'cubes', 'pyramids', 'cylinders', 'towers', 'mushrooms', 'trees', 'apparatus', 'torii'.

* 		grid: Choose from 'none', '1x1', '2x2', 'crosses', 'dots', 'xlines', 'ylines'.
* 		gridColor: Any color value - Color of the grid.


Think very carefully on what the environment of the {input} looks like, and then return the string in this format environment = "preset: forest; groundColor: #445; grid: cross" . THIS IS FORMAT IS VERY IMPORTANT ONLY RETURN IN THIS FORMAT. AND JUST GIVE ME THE OUTPUT WITHOUT ANY TEXT BEFORE OR AFTER THIS IS VERY IMPORTANT '''},
                {"role": "user", "content": input_data.message}
            ]
        )
      

    # Extract the environment configuration from the response
    full_response = response.choices[0].message.content.strip()
    print(full_response)
    environment_config = full_response.split('=')[1].strip().strip('"')
    print(full_response)

    # Render the HTML with the environment configuration
    env_config = EnvironmentConfig(configuration=environment_config)
    template = env.get_template('basic-chat.html')
    rendered_html = template.render(environment_config=environment_config, assets=environment_data)

    # Save the rendered HTML to a file
    output_path = 'examples'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    with open(os.path.join(output_path, 'scene_output.html'), 'w') as file:
        file.write(rendered_html)

    return {"message": "Environment created successfully, HTML file saved."}




# Function to process the GPT response
import json
import logging
import json
import logging

import json
import logging

def process_gpt_response(response):
    """
    Process the GPT response to extract environment data.

    Args:
    - response (str): The response string from GPT.

    Returns:
    - dict: A dictionary with model URLs as keys and lists of positions as values.
    """

    environment_data = {}

    try:
        logging.info(f"Raw GPT response: {response}")
        print(response)
        parsed_response = json.loads(response)
        print(parsed_response)
        logging.info(f"Parsed GPT response: {parsed_response}")

        for model_url, positions in parsed_response.items():
            logging.info(f"Model URL: {model_url}, Positions: {positions}")

            # Check if positions are a list of coordinates or a single coordinate
            if isinstance(positions, list):
                # If positions is a list of lists (coordinates)
                if all(isinstance(pos, list) and len(pos) == 3 for pos in positions):
                    environment_data[model_url] = positions
                # If positions is a single list (single coordinate)
                elif len(positions) == 3 and all(isinstance(coord, (int, float)) for coord in positions):
                    environment_data[model_url] = [positions]
                else:
                    logging.error(f"Unexpected format for positions at model_url: {model_url}, positions: {positions}")
            else:
                logging.error(f"Positions not in list format at model_url: {model_url}, positions: {positions}")

    except json.JSONDecodeError as e:
        logging.error(f"Error parsing the GPT response as JSON: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

    return environment_data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)