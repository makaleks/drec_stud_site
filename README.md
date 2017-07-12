# Department of Radio Electronics and Cybernetics student site

This branch made to run [DEMO](https://drec-stud-site.herokuapp.com/), adopted to run at Heroku free hosting.

### Development

> All changes in code at master should be merged with this branch

1. Clone the repository:
```bash
git clone https://github.com/makaleks/drec_stud_site
```
2. Set up PostgreSQL (note: Django expects UTF-8)
```sql
CREATE DATABASE drec_stud_site;
CREATE USER drec_stud_site_admin;
GRANT ALL PRIVILEGES ON DATABASE drec_stud_site TO drec_stud_site_admin;
```
