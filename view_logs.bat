@echo off
chcp 65001 > nul
echo.
echo ==========================================
echo    CoolMessenger 로그 뷰어
echo ==========================================
echo.
echo 1. 최근 로그 보기 (50줄)
echo 2. 실시간 로그 모니터링
echo 3. 에러 로그만 보기
echo 4. 오늘 로그만 보기
echo 5. 로그 파일 통계
echo 6. 로그 파일 정리
echo 7. 종료
echo.
set /p choice="선택하세요 (1-7): "

if "%choice%"=="1" (
    echo.
    echo 📋 최근 로그 50줄 출력 중...
    python log_viewer.py --tail 50
    pause
) else if "%choice%"=="2" (
    echo.
    echo 📊 실시간 로그 모니터링 시작... (Ctrl+C로 종료)
    python log_viewer.py --follow
) else if "%choice%"=="3" (
    echo.
    echo ❌ 에러 로그만 출력 중...
    python log_viewer.py --level ERROR
    pause
) else if "%choice%"=="4" (
    echo.
    echo 📅 오늘 로그만 출력 중...
    for /f "tokens=1-3 delims=/" %%a in ('date /t') do set today=%%c-%%a-%%b
    python log_viewer.py --date %today%
    pause
) else if "%choice%"=="5" (
    echo.
    echo 📊 로그 파일 통계 생성 중...
    python log_viewer.py --stats
    pause
) else if "%choice%"=="6" (
    echo.
    echo 🧹 로그 파일 정리...
    python log_viewer.py --clear
    pause
) else if "%choice%"=="7" (
    exit /b 0
) else (
    echo 잘못된 선택입니다.
    pause
)

goto :eof
