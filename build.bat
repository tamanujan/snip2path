@echo off
echo === snip2path Windows Build ===

:: 依存ライブラリのインストール
echo Installing dependencies...
python -m pip install -r requirements.txt
python -m pip install pyinstaller

:: ビルド実行
echo Building...
pyinstaller ^
  --windowed ^
  --onedir ^
  --name snip2path ^
  --clean ^
  main.py

echo.
echo Build complete: dist\snip2path\snip2path.exe
pause
