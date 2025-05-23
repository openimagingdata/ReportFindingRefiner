# TODO.md

## Things to refactor
1. Template handling for prompt generation
    - see FMF, prompt_template.py
    - constructor for loading and building the prompt to clean up main.py
2. Database connection
   - right now database connection and dis-connect is not really being handled well

# Write some tests!
- both for testing purposes but also potentially for integrating validated FM's or ground-truth from RadElement to guide LLM output (think few shot learning, RLAIF, etc...)

# Docker-ize!
https://github.com/valiantlynx/ollama-docker
- reference this for a compose setup