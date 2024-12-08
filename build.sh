set -o errexit

pip install -r requirements.txt

python backend/manage.py collectstatic --no-input

python backend/manage.py migrate


if [[ $CREATE_SUPERUSER ]]
then
    python backend/manage.py createsuperuser --no-input \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --email "$DJANGO_SUPERUSER_EMAIL" \
        --password "$DJANGO_SUPERUSER_PASSWORD" \
        --first_name "Admin" --last_name "User"
fi