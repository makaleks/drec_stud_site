# Department of Radio Electronics and Cybernetics student site
This is the repository for [frtk.mipt.ru](https://frtk.mipt.ru/). All users of this department of [MIPT](https://mipt.ru/en/) are able to log in using VK social network. The adaptive design is used. Use the [issues](https://github.com/makaleks/drec_stud_site/issues/) tab to send any bug-reports, or find and contact developers directly before the development is finished :)

All comments, application and command names are made in English, so the materials of this project can be used anywhere else.

We use authorization via [VK](https://vk.com/) social network, so many scripts may use VK API. The `python-social-auth` package is used so other social networks (Fb, etc.) may be adopted in a similar way.

## Requirements

- Python3
- PostgreSQL
- Nginx
- https-connection (highly recommended)

## Branch review

- [pda11111](https://github.com/makaleks/drec_stud_site/tree/pda11111/)- design
- [auth](https://github.com/makaleks/drec_stud_site/tree/auth/) - authorization
- [news](https://github.com/makaleks/drec_stud_site/tree/news/) - news
- [survey](https://github.com/makaleks/drec_stud_site/tree/survey/) - surveys
- [service](https://github.com/makaleks/drec_stud_site/tree/service/) - services (used by washing room, room for meetings, etc.)
- [helpers](https://github.com/makaleks/drec_stud_site/tree/helpers/) - utils, design updates, admin panel updates, general fixes
- [master](https://github.com/makaleks/drec_stud_site/tree/master/) - united result
- [heroku-hosting](https://github.com/makaleks/drec_stud_site/tree/heroku-hosting/) - very outdated, but contains some essential fixes to run on Heroku hosting

## Development

This repository contains copies of some open libraries to be independent from CDN and send these files faster inside university local network:
* normalize.css@7.0.0 (css)
* jquery-3.2.1.min.js (javascript)
* Comfortaa           (font)
* Open Sans           (font)
* ckeditor-4.7        (text editor)
* surveyjs-0.12.23    (survey editor & renderer)
* vk_openapi-573      (VK-social network functions)
* xlsxjs-0.14.0       (Excel table loader)
* vuejs-2.5.17        (frontend framework!)

All license files are available, this libraries are just linked, we are not their authors. 

The project uses **Python3**. 
If `pip` gets crazy and downloads python2 packages, use `pip3`

If you have to start project on CentOS-6, see centos6\_notes.txt to find commands to install newer PostgreSQL and Python3.

0. Don\`t forget to create `setting_additions.py` with any values, see **Project structure** below for details.

1. Clone the repository:
```bash
git clone https://github.com/makaleks/drec_stud_site
cd drec_stud_site
```
2. (Optional, but recommended) Install and run `virtualenv` to create your own virtual Python enviroment (`pip` will not require `sudo`) and enter it:
```bash
virtualenv env
source env/bin/activate
```
> For `fish` shell use `source env/bin/activate.fish`  
> If you get other error at `source` command, try other shell (worked on *bash*, *zsh*)  
3. Install all Python dependences
```bash
pip install -r src/requirements.txt
```
4. To serve static files install Nginx. You must have in /etc/nginx/nginx.conf inside `server{}` (replace `{your_path}` with path to project):
```nginx configuration file
# Check the port - it should be similar to mentioned in gunicorn
# Check you\`ve commented previous `location /`
http {
    include       mime.types;
    # I don`t know what 'default_type' means
    default_type  application/octet-stream;
    sendfile        on;
    server {
        listen       80;
        server_name  localhost;

        # So files > 20M can be loaded.
        client_max_body_size 10m;
        # Always set header to the current host (no url)
        proxy_set_header Host $host;

        location / {
            proxy_pass http://localhost:8080;
        }
        location /robots.txt {
            alias /home/{your_path}/drec_stud_site/collected_static/robots.txt;
        }
        location /static/ {
            alias /home/{your_path}/drec_stud_site/collected_static/;
        }
        location /media/ {
            alias /home/{your_path}/drec_stud_site/media/;
        }
    }
}
```
> If you are running Ubuntu and need to restore default /etc/nginx, run  
> `sudo apt-get purge nginx nginx-common nginx-full`  
> `sudo apt-get install nginx`  
> We strongly recommend to use HTTPS-connections!
5. Don`t forget to run Nginx and PostgreSQL (PostgreSQL is recommended to be newer). You may also want to enable them (run on starup), also before its first start Postgres requires [installation](https://wiki.archlinux.org/index.php/PostgreSQL#Installing_PostgreSQL):
```bash
sudo systemctl start nginx
sudo systemctl start postgresql

sudo systemctl enable nginx
sudo systemctl enable postgresql
```
If your init system is SystemV (not systemd), the following commands will be used (check commands for your distributive):
```bash
sudo /etc/init.d/nginx start
sudo service postgresql restart

sudo chkconfig nginx on
sudo chkconfig postgresql on
```
6. Enter pgsql shell and set up PostgreSQL database for site (note: Django expects UTF-8)
```sql
CREATE DATABASE drec_stud_site;
CREATE USER drec_stud_site_admin;
GRANT ALL PRIVILEGES ON DATABASE drec_stud_site TO drec_stud_site_admin;
```
7. Migrate all your models (don`t forget moving to src/):
```bash
cd src/
./manage.py makemigrations
./manage.py migrate
```
> If you got errors during `makemigrations`:  
> 1. If you got 'virtualenv is not compatible with this system', try recreating `env/` (delete the previous one), providing the most full name of your python, like:  
> `virtualenv -p python3.6 env`  
> 2. If you got some Postgres-related error, like 'peer authentitation failed', try to replace the authentication method for IPv4 local connection METHOD to 'trust' at *pg\_hba.conf* (see where *ph\_hba.conf* is placed in your distribution, may require `sudo ls` to find):  
> `# "local" is for Unix domain socket connections only`
> `host		all		all						trust`  
> `# IPv4 local connections`  
> `host		all		all		127.0.0.1/32		trust`  
> Then restart Postgres:  
> `sudo systemctl restart postgresql`  
>
> If you got errors during 'migrate', try detecting Django apps separately:  
> `manage.py makemigrations user`  
8. (Optional) If you have a *.zip* of backup and wish to insert some data for demonstration, run:
```bash
./postgresql_helper.py -r *yourfile.zip*
```
> run with --help argument to show all arguments  
9. Don`t forget to collect static files from all applications:
```bash
./manage.py collectstatic
```
10. Create a Django superuser (password is required only for superusers):
``` bash
./manage.py shell
from user.managers import UserManager
from user.models import User
m = UserManager()
m.model = User
m.create_superuser('Lastname', 'Firstname', 'Patronymicname', *drec group number*, '*phone number*', '*vk-id number*', '*password*', '*email (optional)*')
```
> Make sure your strings a valid (see `get\_all\_errors()` in `src/user/models.py`)
> We don\`t use any passwords, so simple way doesn\`t work:  
> "manage.py createsuperuser"  
11. Start gunicorn to run Gunicorn server:
```bash
gunicorn --reload -b localhost:8080 -w 4 --pythonpath src drec_stud_site.wsgi:application
```
In addition, a simple `gunicorn-background.service` provided to run the server via systemd. If you have SystemV init system, see `gunicorn-background`. These files need to be placed in appropriate directories of /etc/ and edited for your paths.  
Now, you can view [the site](localhost) at localhost and play with models in [admin panel](localhost/admin) at localhost/admin after login. Moreover, you are able to access static files in `collected static` and `media` using links `localhost/static/FILENAME` and `localhost/media/FILENAME`. Good luck!
12. (Optional) If you have some styles to apply, add configs and build styles.  
The config example layout:
```
config/
├── img/
│   ├── background.svg
│   ├── error.svg
│   └── header.svg
└── _theme.sass
```
Example of `_theme.sass`
```sass
$_primary: #427582
$_primary_font: #fff
$_primary_active: #213a40
$_primary_active_font: #fff
$_primary_disable: #333
$_primary_disable_font: #fff
$_dark: #213a40
$_dark_font: #000
$_secondary: #ffffff
$_background: "../img/background.svg"

$_header: #213a40
$_menu: #213a40
```
Then build new styles. They will appear at `templates-gen` in root directory. Make sure you use virtualenv, if set up on *step 2*. Copy `templates-gen/static/` content in `src/static/`, then collect static files:
```bash
cd swdc/
python gen.py
cd ../
cp templates-gen/static/* src/static/
cd src/
./manage.py collectstatic
```

### Notes
* If you add ordering to already-existing objects, don\`t forget to run command for initial ordering.
```bash
./manage.py reorder note.Note
```
* If you add revisions to already-existing objects, don\`t forget to run command for initial revisions. 
```bash
./manage.py createinitialrevisions
```

## Project structure

The project root directory contains directories of design static pages (swdc), their adaptation to Django with all site logic (src) and files - scripts-tools.

Attention: all projects have some secret data, that can`t be published anywhere. This project has such secrets (+ non-secret 'Debug' flag). You have to set the next fields (use your own values):

```python
# vk.com social network
SOCIAL_AUTH_VK_OAUTH2_KEY = '000'
SOCIAL_AUTH_VK_OAUTH2_SECRET = 'SecretSecret'
# Default values
QUESTION_DEFAULT_APPROVED = True
# Default secrets
DEBUG = True
SECRET_KEY = 'DefaultDjangoSecretNeverUsed'
# Emergency mode: use passwords if SocialAuth is not available
IS_EMERGENCY_LOGIN_MODE = False
# If vk.com stopped giving id by name
IS_ID_RECOGNITION_BROKEN_VK = False
# Redirect to question on each admin access
IS_AGRESSIVE_QUESTION_NOTIFICATION = True
# https://money.yandex.com/
PAYMENT_TEXT_YANDEX = 'The wallet for student council site.'
PAYMENT_YANDEX_ENABLE_CARD = True
PAYMENT_YANDEX_ENABLE_PHONE = False
PAYMENT_SUCCESS_REDIRECT_YANDEX = 'http://localhost/services/'
PAYMENT_SECRET_YANDEX = 'YandexMoneySecret'
PAYMENT_ACCOUNT_YANDEX = 'YandexAccount'

WEBMASTER_TAG_YANDEX = '<meta...'
WEBMASTER_TAG_GOOGLE = '<meta...'

# OPTIONAL

SITE_TAB_NAME = 'Student council'
```

### Scripts-tools

All scripts have `--help` option to show all available arguments.

> OUTDATED: use /admin/user/user/add_many/ admin page to add many users
> `xlsx_helper.py` - script to load users from Microsoft `.xlsx` files (note: not old `.xls`!). It will create `users_parsed.txt` - the JSON file of users that can be used by `manage.py loadusers ../users_parsed.txt` (don\`t forget to load virtualenv via `source ` command and `cd src`). It tries to recognize the fields from the `.xlsx` file and fill `user_errors.txt` if some errors occurred and `user_todo.txt` if some fields are filled and some are not. You may set the cell - start of parsing, the preview will help you to check if all was recognized properly.

`restore_helper.sh` - creates backup of PostgreSQL `.sql` file, `media` and `collected_static` directories, making a `zip` archive, and restores from it. Uses `pgdump_helper.py`. If you need to migrate to other host or everything got crashed/removed, but you have a backup and access to [GitHub](https://github.com/makaleks/drec_stud_site), you need only to clone the code and use this script to restore from backup to get a ready-to-use website (note: this does not set up the enviroment - Nginx config, Postgres user, Python packages, use steps 2-6 in **Development** guide above).

`pgdump_helper.py` - creates a PostgreSQL backup and restores from it.

If you wish to use any of these scripts in your projects, the required changes will be minimal. 

### Design

[swdc](swdc/README.md) - Site Without Django layout Code (only html, css, js and media). 

Use `build.sh` to collect all css styles into fresh content.css. 
Use `preview.sh` to collect all frontend data to view design without development integration (no Python, Django, Gunicorn, Nginx, Postgres - only Linux required). 

[TODO list](swdc/TODO.md)

### Applications

`drec_stud_site` contains `settings.py` and `urls.py` - the Django settings file and root URL path encoder respectively. `settings.py` uses some private settings from `setting_additions.py`  
`html/core` contains basic base template for all site pages.  
`utils` contains some general tools that may be used in any application (validators, database and template context tools, template filters, `manage.py` commands)  
`static` stores all site static files, that can be accessed via `https://frtk.mipt.ru/static/`  
All other directories contain Django applications with names same as web-page functionality.  

The `manage.py` file is the main Django script file, it is installed with Django. 
