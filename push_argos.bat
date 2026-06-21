@echo off
cd /d C:\ARGOS_AI

git status
git add .

git commit -m "Update ARGOS AI"
git push

echo ARGOS PUSH COMPLETE
pause