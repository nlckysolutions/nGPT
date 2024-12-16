# nGPT
A simple, powerful, local, and open source AI.
# About
nGPT was created for a few reasons:
1. Companies like OpenAI are trying to make it harder to run AI locally.
2. There wasn't really an easy way to have an AI do more things besides a few simple ones
3. I want more people to have access to a simple, open-source, local AI that can do many things.

# Features

As of now, the latest publicly-available model of nGPT (nGPT 2M) has the current features:
1. A nice, web hosted Flask Python UI.
2. The ability to search the web.
3. The ability to generate songs (via DeepAI and Selenium + Undetected Chromedriver).
4. The ability to turn on/off your WIZ smart lights with no additional setup required.

# Installation

## Method 1: LM Studio (WINDOWS)
To begin, please run the following command in a Powershell (WINDOWS ONLY):

```iwr "https://raw.githubusercontent.com/nlckysolutions/nGPT/main/windows-installer.bat" -OutFile "$env:TEMP\wi.bat"; &$env:TEMP\wi.bat```

Afterwards, you should be greeted with the console-based installer, then follow the prompts to install LM Studio, all the required models and data, and nGPT.

**LINUX is currently not supported, however it will be in the future.**

**I do NOT and will NOT support MacOS. This is mostly due to Apple's prices, ecosystem, and locking down devices with "Activation Lock", as well as doing many other money-generating practices which other companies unfortunately follow. In order to combat this, I do not want to make anything available for their product(s) as a sort of 'strike.' If you would like to test nGPT on MacOS, please run Windows or Linux with Parallels or another VM program.**
