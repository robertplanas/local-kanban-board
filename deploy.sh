rm -rf build dist *.spec
.venv/bin/python -m PyInstaller --noconfirm --windowed --icon="./auxiliar/app.icns" --add-data="templates:templates" --name="Personal Kanban" web.py