Apache + mod-wsgi configuration
===============================

An example Apache2 vhost configuration follows::

    WSGIDaemonProcess token_supplier-<target> threads=5 maximum-requests=1000 user=<user> group=staff
    WSGIRestrictStdout Off

    <VirtualHost *:80>
        ServerName my.domain.name

        ErrorLog "/srv/sites/token_supplier/log/apache2/error.log"
        CustomLog "/srv/sites/token_supplier/log/apache2/access.log" common

        WSGIProcessGroup token_supplier-<target>

        Alias /media "/srv/sites/token_supplier/media/"
        Alias /static "/srv/sites/token_supplier/static/"

        WSGIScriptAlias / "/srv/sites/token_supplier/src/token_supplier/wsgi/wsgi_<target>.py"
    </VirtualHost>


Nginx + uwsgi + supervisor configuration
========================================

Supervisor/uwsgi:
-----------------

.. code::

    [program:uwsgi-token_supplier-<target>]
    user = <user>
    command = /srv/sites/token_supplier/env/bin/uwsgi --socket 127.0.0.1:8001 --wsgi-file /srv/sites/token_supplier/src/token_supplier/wsgi/wsgi_<target>.py
    home = /srv/sites/token_supplier/env
    master = true
    processes = 8
    harakiri = 600
    autostart = true
    autorestart = true
    stderr_logfile = /srv/sites/token_supplier/log/uwsgi_err.log
    stdout_logfile = /srv/sites/token_supplier/log/uwsgi_out.log
    stopsignal = QUIT

Nginx
-----

.. code::

    upstream django_token_supplier_<target> {
      ip_hash;
      server 127.0.0.1:8001;
    }

    server {
      listen :80;
      server_name  my.domain.name;

      access_log /srv/sites/token_supplier/log/nginx-access.log;
      error_log /srv/sites/token_supplier/log/nginx-error.log;

      location /500.html {
        root /srv/sites/token_supplier/src/token_supplier/templates/;
      }
      error_page 500 502 503 504 /500.html;

      location /static/ {
        alias /srv/sites/token_supplier/static/;
        expires 30d;
      }

      location /media/ {
        alias /srv/sites/token_supplier/media/;
        expires 30d;
      }

      location / {
        uwsgi_pass django_token_supplier_<target>;
      }
    }
