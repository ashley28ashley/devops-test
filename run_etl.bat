@echo off
set PGCLIENTENCODING=UTF8
python etl/loader.py
pause