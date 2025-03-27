@echo off
echo 正在创建桌面快捷方式...
pip install winshell pywin32 -i https://pypi.tuna.tsinghua.edu.cn/simple >nul 2>&1
python desktop.py
if errorlevel 1 (
    echo 创建失败，请确保已安装Python和必要的依赖
    pause
) 