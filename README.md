# django_curate

# About
This project is an attempt to create a python-django based site for curators/users to submit gene annotations for the Planteome project. An initial version was create using Drupal, but was found to not scale well so this was written from scratch.

# Install
## Prerequisites
This project requires Docker to already be installed and configured. Docker-compose is also required. See notes below if using podman instead of docker.

Development is done using the Professional version of PyCharm from JetBrains. The free versions do not support Docker and Django for debugging.
To set up PyCharm to use Docker as a remote interpreter, follow the instructions at https://www.jetbrains.com/help/pycharm/using-docker-compose-as-a-remote-interpreter.html#configuring-docker


A `.env` file is required in the root directory of the project. It should at least contain the following:
```
MYSQL_NAME=
MYSQL_USER=
MYSQL_HOST=db
MYSQL_PASSWORD=

DEBUG=True #False
ALLOWED_HOSTS=curate.planteome.org #FQDN. Use '*' for wildcard but only in debug mode
CSRF_TRUSTED_ORIGINS=https://*.planteome.org,https://*.127.0.0.1

DJANGO_SECRET_KEY=

ORCID_clientID=
ORCID_secret=

ENTREZ_EMAIL=""
ENTREZ_API_KEY=

ELASTICSEARCH_DSL_HOSTS=es:9200

AMIGO_BASE_URL="https://browser.planteome.org/"
```
with your own values for each. The Entrez API info can be found by following https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/.

## Run

### Configuration
Some changes to docker-compose.yml may be required for the database to connect and start properly. Specifically, the volumes may need to be set.

### Initial setup
After pulling the repo from git, some steps will need to be followed to initialize the database for the first use.
1. Some changes to docker-compose.yml may be required for the database to connect and start properly. Specifically, the volumes may need to be set.
2. Run `docker compose run -d -e MARIADB_ROOT_PASSWORD=password -e MARIADB_DATABASE=curate_web -e MARIADB_USER=curate-user -e MARIADB_PASSWORD=password db` from the directory where the repo was downloaded. This will initialize a MySQL(Mariadb).
Note: this should just work from the values in the .env file, but doesn't for some reason. Didn't figure out why.
3. Stop the container. Get the continer ID from `docker ps`, stop it with `docker stop CONTAINER_ID`.
4. Start all the containers with `docker compose up -d`
5. Verify all containers are running with `docker ps`
6. Get in to the "web" container with `docker compose exec web bash` 
7. Initialize the database with `python manage.py migrate`
8. Set up the superuser with `python manage.py createsuperuser` - follow the prompts
9. The account just created will need to be approved before use. Exit the docker container and log in to the mysql with `mysql -u root -p -P 3307 -h 127.0.0.1`
    ```
    use curate_web;
    update accounts_user set is_approved = 1, role = 'Superuser', orcid = 'your_valid_orcid', affiliation = 'whatever', first_name = '', last_name = '' where id = 1;
    ```
10. Add the callback URL (site/oidc/callback) to ORCID developer tools (https://orcid.org/developer-tools)
11. May need to fix the permissions for the docker volumes for mysql and elasticsearch. Temporarily set them to be world-writeable, figure out the user that is writing to them, and change the ownership.


# Usage
When running, the site should be available at http://localhost:8000.

After accounts, the following should also be imported:
```
taxonomy
dbxrefs
genes
annotations
```
Genes must be imported after taxonomy, and annotations after genes.

More info on doing this will be added to this doc later.


## Using podman instead of docker
Assumes podman is already installed.

Additional steps if using podman instead of docker:

1. Set up the sub{uids,gids}.
   ```
      sudo usermod --add-subuids 100000-100999 username
      sudo usermod --add-subgids 100000-100999 username
   ```
2. Optional: Change the container storage location by adding the file ~/.config/containers/storage.conf with the following:
   ```
      [storage]
      driver = "overlay"
      graphroot = "/data/podman"
   ```
3. Run the migrate tool with `podman system migrate`
4. Instead of using `docker` use `podman` and `podman-compose` instead of `docker compose`

Notes: It might ask from where to download the images from. I chose docker.io for each, but I don't think it matters.

Also, the permissions for the mariadb and elasticsearch volumes may need to be changed. I did it with:
```
sudo chown -R 100999:jaiswallab /data/docker_volumes/curate/es
sudo chown -R 100998:100998 /data/docker_columes/curate/mysqldata
```
