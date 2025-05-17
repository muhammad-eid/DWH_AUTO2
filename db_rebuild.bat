@echo off


:MENU
echo.
echo Select an option:
echo 1. Run app with Streamlit
echo 2. Rebuild DB
echo 3. Exit
set /p choice=Enter your choice (1-3): 

if "%choice%"=="1" (
    streamlit run Vodafone.py
    goto MENU
) else if "%choice%"=="2" (
    REM Remove all files from data/db except .sql files
    for %%f in ("data\db\*") do (
        if /I not "%%~xf"==".sql" del "%%f"
    )

    REM Run the Python script to rebuild the database
    python services/db_local_service.py
    goto MENU
) else if "%choice%"=="3" (
    exit /b
) else (
    echo Invalid choice. Please try again.
    goto MENU
)