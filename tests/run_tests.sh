@echo off
echo === Tests Python ===
python -m pytest

echo.
echo === Tests Node.js ===
npm test

echo.
echo === FIN DES TESTS ===
pause