set -o errexit

pip install -r requirements.txt

python backend/manage.py collectstatic --no-input

python backend/manage.py migrate


if [[ $CREATE_SUPERUSER ]]
then
    python backend/manage.py shell <<EOF
from django.contrib.auth import get_user_model
from django.core.management import call_command

User = get_user_model()

# Create the superuser
User.objects.create_superuser(
    username='$DJANGO_SUPERUSER_USERNAME',
    email='$DJANGO_SUPERUSER_EMAIL',
    password='$DJANGO_SUPERUSER_PASSWORD',
    first_name='Admin',  # You can also set this via environment variable
    last_name='User'     # You can also set this via environment variable
)
EOF
fi