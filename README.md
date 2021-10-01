# django_curate

# About
This project is an attempt to create a python-django based site for curators/users to submit gene annotations for the Planteome project. An initial version was create using Drupal, but was found to not scale well so this was written from scratch.

# Install
## Prerequisites
This project requires Docker to already be installed and configured. Docker-compose is also required.

Development is done using the Professional version of PyCharm from JetBrains. The free versions do not support Docker and Django for debugging.
To set up PyCharm to use Docker as a remote interpreter, follow the instructions at https://www.jetbrains.com/help/pycharm/using-docker-compose-as-a-remote-interpreter.html#configuring-docker


A `.env` file is required in the root directory of the project. It should at least contain the following:
```
MYSQL_NAME=
MYSQL_USER=
MYSQL_HOST=db
MYSQL_PASSWORD=

DJANGO_SECRET_KEY=

ENTREZ_EMAIL=""
ENTREZ_API_KEY=
```
with your own values for each. The Entrez API info can be found by following https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/.

## Run
Assuming Docker is configured correctly, easiest thing to do is run `docker-compose up` from the directory where the git repo was downloaded

## Configuration
Some changes to docker-compose.yml may be required for the database to connect and start properly. Specifically, the volumes may need to be set.
If starting from scratch (no existing database), the django command `python manage.py makemigrations` and `python manage.py migrate` will need to be run to set up the database.

# Usage
When running, the site should be available at http://localhost:8000.

Accounts will need to be created. The initial account may need to be created from the django terminal. The rest can be created and approved via the site.

After accounts, the following should also be imported:
```
taxonomy
dbxrefs
genes
annotations
```
Genes must be imported after taxonomy, and annotations after genes.

More info on doing this will be added to this doc later.
