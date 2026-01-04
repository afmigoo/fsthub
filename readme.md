# FSThub - a hub for Helsinki transducers (HFST)

A web app that allows users to interact with .hfst(ol) transducers, to provide a text input and recieve it's text output. It uses Django (frontend, API) and sqlite (metadata storage).

The app comes with a an API, which also can be used independently from the frontend for FST interaction.

## Quick start
### Docker
You can use the provided docker-compose.yml and just run
```shell
docker compose up -d
```
### Without Docker
To run the app without docker, first, install all the python dependencies:
> Note that this example does not include any virtual environment handling instructions. The command below will install all python dependencies at global scope which is not recommended!
```shell
pip install -r requirements.txt
```
Then, install [HFST toolkit](https://github.com/hfst/hfst). The example below can be used on Debian-like systems, if your system differs, please, follow official installation instructions.
```shell
apt install hfst
```
You can verify now that everything works by running tests:
```shell
cd fsthub && python3 manage.py test
```

Finally, you run the app any way you want. Below are a couple of examples you could use:
```shell
# Recommended way
cd fsthub && uwsgi --http :8000 --wsgi-file fsthub/wsgi.py
# Run dev server (not recommended for production)
python3 fsthub/manage.py runserver
```
### Transducer binaries
The app stores all it's variable data in `./data/` directory (path relative to the repository's root)
```
data
├── db.sqlite3      # created automatically
└── hfst_projects
    ├── project_1
    │   ├── something_generator.hfstol
    │   ├── ...
    │   └── something_translit.hfstol
    ├── ...
    └── project_n
        ├── something_analyzer.hfstol
        ├── ...
        └── something_translit.hfstol
```
The directory `./data/hfst_projects/<project>/` is where you put all your hfst binaries. If you do not have project distinction with your set of binaries, you can create a single general project `./data/hfst_projects/all/` for an example, and place all binaries there.  

You can see a minimal example in `./data_example`. It contains a single project with a pre-compiled transducer that takes 'ping' and returns 'pong'.

---
2025  
Author: Elen Kartina
