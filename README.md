# Aelfgpt

[Live app](https://aelfgpt.streamlit.app/)

AelfGPT is a GPT chat model perfectly geered towards the Aelf blockchain developers with the aim to soften development burden on the developers.

Just like ChatGPT, but for Aelf.

## Demo
![alt text](assets/aelfgpt-1.png "AelfGPT demo 1")
![alt text](assets/aelfgpt-2.png "AelfGPT demo 2")

## Technologies

This application was brought to life using the following technologies

1. Gemini
2. Atlas MongoDB
3. Llama Index
4. Streamlit

## Setup

*Option 1*

Use Gitpod: go to [https://gitpod.io/#https://github.com/balojey/aelfgpt](https://gitpod/#https://github.com/balojey/aelfgpt)

All dependencies will be installed automatically

*Option 2*

Clone this repo: `git clone https://github.com/balojey/aelfgpt`

Then, install dependencies: `poetry install`

## Run AelfGPT

Populate your environment variables

```
    ATLAS_URI=
    LLAMA_API_KEY=
```

Then, run: `poetry run streamlit run src/AelfGPT.py`