@echo off
REM Create implementation folder
if not exist implementation mkdir implementation
echo ✅ Created implementation folder

REM Move markdown files
if exist HTTPS_IMPLEMENTATION.md move HTTPS_IMPLEMENTATION.md implementation\ && echo ✅ Moved HTTPS_IMPLEMENTATION.md
if exist HTTPS_MIGRATION.md move HTTPS_MIGRATION.md implementation\ && echo ✅ Moved HTTPS_MIGRATION.md
if exist MIGRATION_GUIDE.md move MIGRATION_GUIDE.md implementation\ && echo ✅ Moved MIGRATION_GUIDE.md
if exist MIGRATION_SUMMARY.md move MIGRATION_SUMMARY.md implementation\ && echo ✅ Moved MIGRATION_SUMMARY.md
if exist QUICKSTART.md move QUICKSTART.md implementation\ && echo ✅ Moved QUICKSTART.md
if exist QUICK_MIGRATION_REFERENCE.md move QUICK_MIGRATION_REFERENCE.md implementation\ && echo ✅ Moved QUICK_MIGRATION_REFERENCE.md
if exist ROLES_GUIDE.md move ROLES_GUIDE.md implementation\ && echo ✅ Moved ROLES_GUIDE.md

echo.
echo ✅ All implementation docs moved to implementation/ folder!
pause
