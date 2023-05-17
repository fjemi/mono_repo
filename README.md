# Mono Repo
Attempting to combine other repos and some local development into a single mono repo. 

# Useage
- After cloning the repo, run `pipenv install` from the root folder to install dependencies. 
- Create an `.env` file based on the `env.example` file in the root folder.
- Run `pipenv run startup` to start the API server.
- Navigate to `localhost:8000/docs` in a browser to view the API's OpenAPI documentation

# TODO
- Merge in existing repos: want to preserve the history of some of the repos as the files in this repo are a refactor of code from the old repo.
- API Authentication/Authorization
- Add wrappers for external Python packages
- Testing Framework: working on a no to low code data/yaml driven testing framework. Instead of writing tests, data to run tests are defined in yaml file (`app_test.yml`). Input data in the yaml are run through functions, apps, integrations, etc and we just need to verify that the outputs match the expected out put in the yaml file. This is mostly done, just need to update the files in the tests directory and finalize the format of the test yaml files.