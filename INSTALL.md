# Installation

## Backend

To install the backend, add `trovastelle.service` as a systemd service.

1. Install the Python requirements for Trovastelle with `python -m pip install -r requirements.txt` in the root folder of this repo.
1. Install the package with `python -m pip install -e .` in the root folder of this repo. Note that `-e` symlinks the package to the current folder instead of copying, which is a good idea for development.
1. Ensure that the paths in `trovastelle.service` and `trovastelle.sh` in the `/src/celestial-compass/` folder match the path where this folder is.
1. Copy `trovastelle.service` in the `/src/celestial-compass/` folder to /`etc/systemd/system`.
1. Run `systemctl enable trovastelle`
1. Run `systemctl start trovastelle`

## Frontend

To install the frontend:

1. Copy `trovastelle.wsgi` in the ``/src/celestial-compass/` folder to `/var/www/wsgi-scripts`.
1. Create a file `trovastelle_web.log` in `/var/www/wsgi-scripts` and ensure that it is owned by the `pi` user: `cd /var/www/wsgi-scripts && sudo touch trovastelle_web.log && sudo chown pi trovastelle_web.log`.
1. Compile the frontend with `npm run build` in the `frontend` folder.
1. Copy the frontend installation files in `frontend/build` to `/var/www/frontend`.
1. Ensure that Apache and mod_wsgi are installed.
1. Copy `020-wsgi-backend.conf` to `/etc/apache2/sites-available`. 
1. Run `sudo a2enmod 020-wsgi-backend.conf`.
1. Restart the Apache2 daemon with `sudo systemctl reload apache2`.