# nGPT
A simple, powerful, local, and open source AI.
# About
nGPT was created for a few reasons:
1. Companies like OpenAI are trying to make it harder to run AI locally.
2. There wasn't really an easy way to have an AI do more things besides a few simple ones
3. I want more people to have access to a simple, open-source, local AI that can do many things.

# Features

As of now, the latest publicly-available model of nGPT (nGPT 2M) has the current features (without checkmarks = buggy or in progress):
- [x] A nice, web hosted Flask Python UI.
- [x] The ability to generate songs (via DeepAI and Selenium + Undetected Chromedriver).
- [x] The ability to turn on/off your WIZ smart lights with no additional setup required.
- [ ] List devices on Wi-Fi and Bluetooth
- [ ] The ability to search the web.

# Installation

> [!IMPORTANT]
> ***IT IS STRONGLY AND HIGHLY RECCOMENDED TO HAVE A DEDICATED GPU. OTHERWISE, IT IS NOT ADVISED TO USE nGPT.***

## Method 1: LM Studio (WINDOWS)
- Download and install LM Studio.
- In LM Studio, in the search icon section at the bottom left, type in "Meta-Llama-3-8B-Instruct" and hit CTRL+ENTER.
- Click the first result by LM Studio Community and click download.
- Go into LM Studio and click the console icon.
- Click "Load a Model" at the top.
- Click the model you downloaded (Meta Llama 3 8B Instruct).
- Use default settings and load the model.
- Press CTRL+R to start the server.
- Go back to the GitHub repo, go to Releases, then click on the version of nGPT you wish to install.
- Download the .py file for Windows.
- In the folder that you installed nGPT, open a Command Prompt, CD into that folder, and type ```python app.py```.
- In the Command Prompt window, CTRL+CLICK the first link to be brought to nGPT WebUI.
- Have fun using Experimental nGPT!

> [!TIP]
> Make sure to click the save button in the top-right corner to save your current chat. These will be saved locally so they will always be there. nGPT does not autosave.**

Whenever you want to use nGPT, you will need to load the model and start the server again:
- Go into LM Studio and click the console icon.
- Click "Load a Model" at the top.
- Click the model you downloaded (Meta Llama 3 8B Instruct).
- Use default settings and load the model.
- Press CTRL+R to start the server.
- Go into the folder you have nGPT in, open a Command Prompt, CD into that folder, and type ```python app.py```.
- In the Command Prompt window, CTRL+CLICK the first link to be brought to nGPT WebUI.

> [!NOTE]
> **LINUX is currently not supported, however it will be in the future.**
>
> **I do NOT and will NOT support MacOS. This is mostly due to Apple's prices, ecosystem, and locking down devices with "Activation Lock", as well as doing many other money-generating practices which other companies unfortunately follow. In order to combat this, I do not want to make anything available for their product(s) as a sort of 'strike.' If you would like to test nGPT on MacOS, please run Windows or Linux with Parallels or another VM program.**
