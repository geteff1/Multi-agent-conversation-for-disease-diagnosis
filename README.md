# Multi-agent-conversation-for-disease-diagnosis

## Introduction

This repository presents a novel multi-agent conversation framework designed to enhance the capabilities of Large Language Models (LLMs) in diagnosing complex diseases. Our approach, structured under the Autogen framework, allows for in-depth conversations among LLMs, paving the way for more accurate and nuanced disease diagnosis.

## Preprint Article

Our work has been documented in a preprint article titled "One is Not Enough: Multi-Agent Conversation Framework Enhances Rare Disease Diagnostic Capabilities of Large Language Models". For more insights into our study, please visit: https://www.researchsquare.com/article/rs-3757148/v1

Multi Agent Conversation Flow
![image](https://github.com/geteff1/Multi-agent-conversation-for-disease-diagnosis/assets/148701415/357585db-30b8-487d-83f6-1d8640e9ec38)

**Test Dataset**

302 disease cases were retrieved. Each case was curated as primary consultation and follow-up consultation to test the effectiveness of LLMs in actual clincial scenarios.
![Figure 2](https://github.com/geteff1/Multi-agent-conversation-for-disease-diagnosis/assets/148701415/8762cb39-adaf-42a9-b123-9aef73e578bc)

## Runtime Estimate

The estimated time to run a single case using our framework is approximately 5-10 minutes, varying slightly based on system specifications and network conditions.

## Setup
 * Install anaconda: https://www.anaconda.com/distribution/
 * set up conda environment w/ python 3.8, ex:
    * `conda create --name mac python=3.8`
    * `conda activate mac`
    * `pip install pyautogen==0.2.32`


## Training
You should first set your API, proxy, and corresponding model list in **configs/config_list.json**.
```bash
    {
        "model": "gpt-4o",  # It can be OpenAI's models, or others such as Claude, Gemini, LLaMA 3.1, etc.
        "api_key": "", # your API
        "base_url": "", # base URL
        "tags": [
            "x_gpt4o"
        ]  # You can assign different tags to different models.
    },
```
You can also use locally deployed models, such as oLlama and LiteLLM together. For more details, see "https://microsoft.github.io/autogen/docs/topics/non-openai-models/local-litellm-ollama."
```bash
    {
        "model": "llama3.1", 
        "api_key": "NotRequired",
        "base_url": "http://0.0.0.0:4000",
        "tags": [
            "llama3.1"
        ]
    }
```

All commands should be run under the project root directory.

```bash
sh scripts/train.sh
```

## Evaluation
All commands should be run under the project root directory.

```bash
bash scripts/eval.sh
```

## Results
Results will be saved in a folder named `outputs/`. 

## Contributing

We welcome contributions to this project. If you have suggestions for improvements or want to report issues, please feel free to open an issue or submit a pull request.
