# gpt-engineer-example

Currently fails the "Test Hello World" benchmark.
gpt-engineer has trouble when the repo is empty.

# usage

## prerequisites

In order to run this agent you will need to have the AI Maintainer Platform running locally. You can find instructions on how to do that [here](https://github.com/ai-maintainer-inc/platform-dockerized).

## set up .env

Create a `.env` file from the template:

```
cp .env.template .env
```

Fill in the fields in your `.env` file.
- `OPENAI_API_KEY` is your [OpenAI API key](https://platform.openai.com/account/api-keys).
- `AIM_USERNAME` is your AI Maintainer username. If you don't have an account we will create one for you with this username.
- `AIM_PASSWORD` is your AI Maintainer password. If you don't have an account we will create one for you with this password.
- `AIM_EMAIL` is the email address associated with your AI Maintainer account. If you don't have an account we will create one for you with this email address.
- `AIM_AGENT_NAME` is the name of the agent you want to create. If you don't have an agent with this name we will create one for you.


## set up virtual env

Create a virtual env and install requirements:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## run

Run the script:

```
python main.py
```