web: gunicorn toyota_training.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 30
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput