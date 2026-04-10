@echo off

echo =====================================
echo Starting BigData Environment...
echo =====================================

REM 激活conda环境
call D:\anaconda3\Scripts\activate.bat bigdata

REM 进入你的项目目录
cd /d E:\HAMK\Bigdata

REM 启动Jupyter Lab
jupyter lab

pause