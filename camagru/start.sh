#!/bin/sh

python3 manage.py makemigrations cam
python3 manage.py migrate
python3 manage.py initdata
# python3 manage.py populate
python3 manage.py runserver

# python3 manage.py populate 10
# python3 manage.py collectstatic --no-input
# echo "Starting Daphne server..."
# daphne -b 0.0.0.0 -p 8001 -e ssl:8443:privateKey=/etc/nginx/ssl/key.pem:certKey=/etc/nginx/ssl/cert.pem camagru.asgi:application
# echo "Daphne server started"