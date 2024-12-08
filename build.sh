set -o errexit

pip install -r requirements.txt

python backend/manage.py collectstatic --no-input

python backend/manage.py migrate


if [[ $CREATE_SUPERUSER ]]
then
    python manage.py createsuperuser --no-input
fi