#serve-backend.sh

echo "Sirviendo Backend..."
cd backend

echo "Activando Venv"
source contratista_venv/bin/activate

echo "Desactivado PYTHONPATH"
unset PYTHONPATH

echo "Iniciando Postgresql..."
sudo systemctl restart postgresql

echo "Iniciando Django..."
python manage.py runserver 0.0.0.0:8182