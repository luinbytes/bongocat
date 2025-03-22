@echo off
echo Building Bongo Cat...
pyinstaller --onefile --windowed --add-data "img/*;img/" --clean --noupx bongo_cat.py
echo Build complete!
pause 