@echo off
echo 正在安装依赖包，请稍候...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo 安装失败，请检查网络连接或Python安装状态
) else (
    echo 安装成功！现在可以运行"启动程序.bat"启动应用
)
pause 