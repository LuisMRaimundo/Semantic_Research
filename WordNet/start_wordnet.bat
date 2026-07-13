@echo off
chcp 65001 >NUL
cd /d "%~dp0"
echo Starting Open English Wordnet GUI...
echo (First run downloads the Open English Wordnet; this can take a while.)
python "wordnet_gui_v2.py" %*
if errorlevel 1 (
    echo.
    echo Failed to start. Make sure Python 3.10+ is installed and on PATH, then:
    echo     pip install wn nltk matplotlib networkx
    echo     python -c "import wn; wn.download('oewn:2024')"
    pause
)
