@echo off
echo 正在启动多功能随机工具...
pythonw start.pyw
if errorlevel 1 (
    echo 启动失败，请确保已正确安装Python和依赖包
    echo 可以尝试在命令行中运行: pip install -r requirements.txt
    pause
) 