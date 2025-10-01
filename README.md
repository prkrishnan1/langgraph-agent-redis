### Langgraph Agent App ###

Agent built with weather and web browsing capabilities, deployed with redis backend and streamlit frontend

### Components ####
* Tools: Tavily browser tool, Weather.com api
* Streamlit Interface: Streamlit front-end which supports multiple threads, and persists messages across sessions
* Redis: Self hosted in docker container
* In future: codex

#### Quick Start #### 

`docker compose up`

 - builds agent and redis containers together and provides streamlit app url

