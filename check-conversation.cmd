@echo off
REM Antigravity conversation report by ConversationID
REM Usage: check-conversation.cmd <ConversationID> [--tools --errors --full --list]
setlocal
if "%~1"=="" (
    echo Provide a ConversationID. To list all: check-conversation.cmd --list
    exit /b 2
)
python "%~dp0src\conversation_report.py" %*
exit /b %ERRORLEVEL%
