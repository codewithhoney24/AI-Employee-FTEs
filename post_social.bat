@echo off
rem ------------------------------------------------------------
rem Load environment variables from .env (key=value per line)
rem ------------------------------------------------------------
for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
    set "%%A=%%B"
)

rem ------------------------------------------------------------
rem Ensure the drafts folder exists
rem ------------------------------------------------------------
if not exist drafts (
    mkdir drafts
)

rem ------------------------------------------------------------
rem Create a sample draft if none exists
rem ------------------------------------------------------------
if not exist drafts\today.md (
    echo Hello, world! This is an automated post from my AI Employee. > drafts\today.md
)

rem ------------------------------------------------------------
rem Run the posting script
rem ------------------------------------------------------------
python social_post.py drafts\today.md

rem Keep the window open so you can see the script output
pause