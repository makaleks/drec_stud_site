# Department of Radio Electronics and Cybernetics student site

### Branch review

- pda11111 - design
- auth - authorization
- master - united result

### Design
[swdc](swdc/README.md) - Site Without Django layout Code (only html, css, js and media)
[TODO list](swdc/TODO.md)

### Development

1. Clone the repository:
```bash
git clone https://github.com/makaleks/drec_stud_site
cd drec_stud_site
```
2. (Optional) Install and run 'virtualenv' to create your own virtual Python enviroment ('pip' will not require 'sudo') and enter it:
```bash
virtualenv env
source env/bin/activate
```
3. Install all Python dependences
```bash
pip install -r src/requirements.txt
```
4. To serve static files install Nginx. You must have in /etc/nginx/nginx.conf inside 'server{}':
```nginx configuration file
# So files > 20M can be loaded.
client_max_body_size 10m;
# Check the port - it should be similar to mentioned in gunicorn
# Check you've commented previous 'location /'
http {
    include       mime.types;
    # I don`t know what 'default_type' means
    default_type  application/octet-stream;
    sendfile        on;
    server {
        listen       80;
        server_name  localhost;

        location / {
            proxy_pass http://localhost:8080;
        }
        location /static/ {
            alias /home/dev/drec_stud_site/collected_static/;
        }
        location /media/ {
            alias /home/dev/drec_stud_site/media/;
        }
    }
}
```
5. Don`t forget to run Nginx and Postgres. You may also want to enable them (run on starup), also before its first start Postgres requires [installation](https://wiki.archlinux.org/index.php/PostgreSQL#Installing_PostgreSQL):
```bash
sudo systemctl start nginx
sudo systemctl start postgresql

sudo systemctl enable nginx
sudo systemctl enable postgresql
```
6. Set up PostgreSQL (note: Django expects UTF-8)
```sql
CREATE DATABASE drec_stud_site;
CREATE USER drec_stud_site_admin;
GRANT ALL PRIVILEGES ON DATABASE drec_stud_site TO drec_stud_site_admin;
```
7. Migrate all your models:
```bash
src/manage.py makemigrations
src/manage.py migrate
```
> If you got errors during 'migrate', try detecting Django apps separately:
> "src/manage.py makemigrations user_info"
8. (Optional) If you wish to insert some data for demonstration, run:
```bash
./postgresql_helper.py -r
```
> run with --help argument to show all arguments
9. If you restore database from demonstration backup the default cretentials are "admin, password123". If you did`t, create a Django superuser:
``` bash
src/manage.py createsuperuser
```
10. Don`t forget to collect static files from all applications:
```bash
src/manage.py collectstatic
```
11. Start gunicorn to run Gunicorn server:
```bash
gunicorn --reload -b localhost:8080 --pythonpath src drec_stud_site.wsgi:application
```
Now, you can view [the site](localhost) at localhost and play with models in [admin panel](localhost/admin) at localhost/admin. Moreover, you are able to access static files in 'collected static' and 'media' using links 'localhost/static/FILENAME' and 'localhost/media/FILENAME'. Good luck!
