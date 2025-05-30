#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoolMessenger 로그 뷰어
실시간으로 로그를 확인하고 필터링할 수 있는 도구
"""

import os
import sys
import time
import argparse
from datetime import datetime, timedelta

def tail_log(filename, lines=50):
    """로그 파일의 마지막 N줄을 출력"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return all_lines[-lines:] if len(all_lines) > lines else all_lines
    except FileNotFoundError:
        print(f"❌ 로그 파일을 찾을 수 없습니다: {filename}")
        return []
    except Exception as e:
        print(f"❌ 로그 파일 읽기 오류: {e}")
        return []

def follow_log(filename):
    """실시간으로 로그 파일을 모니터링"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            # 파일 끝으로 이동
            f.seek(0, 2)
            
            print(f"📊 실시간 로그 모니터링 시작: {filename}")
            print("Ctrl+C로 종료하세요.\n")
            
            while True:
                line = f.readline()
                if line:
                    print(line.rstrip())
                else:
                    time.sleep(0.1)
                    
    except FileNotFoundError:
        print(f"❌ 로그 파일을 찾을 수 없습니다: {filename}")
    except KeyboardInterrupt:
        print("\n📊 실시간 모니터링 종료")
    except Exception as e:
        print(f"❌ 로그 모니터링 오류: {e}")

def filter_logs(filename, level=None, date=None, keyword=None):
    """로그를 필터링하여 출력"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        filtered_lines = []
        
        for line in lines:
            # 레벨 필터
            if level and level.upper() not in line:
                continue
                
            # 날짜 필터
            if date:
                if date not in line:
                    continue
                    
            # 키워드 필터
            if keyword:
                if keyword.lower() not in line.lower():
                    continue
                    
            filtered_lines.append(line.rstrip())
            
        return filtered_lines
        
    except FileNotFoundError:
        print(f"❌ 로그 파일을 찾을 수 없습니다: {filename}")
        return []
    except Exception as e:
        print(f"❌ 로그 필터링 오류: {e}")
        return []

def show_log_stats(filename):
    """로그 파일 통계 정보 출력"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        total_lines = len(lines)
        info_count = sum(1 for line in lines if 'INFO' in line)
        error_count = sum(1 for line in lines if 'ERROR' in line)
        warning_count = sum(1 for line in lines if 'WARNING' in line)
        
        file_size = os.path.getsize(filename)
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"📊 로그 파일 통계: {filename}")
        print(f"📁 파일 크기: {file_size_mb:.2f} MB")
        print(f"📄 총 라인 수: {total_lines:,}")
        print(f"ℹ️  INFO: {info_count:,}")
        print(f"⚠️  WARNING: {warning_count:,}")
        print(f"❌ ERROR: {error_count:,}")
        
        if lines:
            first_line = lines[0].strip()
            last_line = lines[-1].strip()
            
            # 첫 번째와 마지막 로그의 시간 추출 시도
            try:
                first_time = first_line.split(' - ')[0]
                last_time = last_line.split(' - ')[0]
                print(f"🕐 첫 로그: {first_time}")
                print(f"🕐 마지막 로그: {last_time}")
            except:
                pass
                
    except FileNotFoundError:
        print(f"❌ 로그 파일을 찾을 수 없습니다: {filename}")
    except Exception as e:
        print(f"❌ 통계 생성 오류: {e}")

def clear_old_logs(filename, days=7):
    """오래된 로그 정리 (백업 후 삭제)"""
    try:
        if not os.path.exists(filename):
            print(f"❌ 로그 파일을 찾을 수 없습니다: {filename}")
            return
            
        # 백업 파일명 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{filename}.backup_{timestamp}"
        
        # 현재 로그를 백업
        import shutil
        shutil.copy2(filename, backup_filename)
        print(f"📦 로그 백업 완료: {backup_filename}")
        
        # 새 로그 파일 생성 (기존 파일 비우기)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# 로그 파일 정리됨 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
        print(f"🧹 로그 파일 정리 완료: {filename}")
        
    except Exception as e:
        print(f"❌ 로그 정리 오류: {e}")

def main():
    parser = argparse.ArgumentParser(description='CoolMessenger 로그 뷰어')
    parser.add_argument('--file', '-f', default='coolmessenger.log', 
                       help='로그 파일 경로 (기본값: coolmessenger.log)')
    parser.add_argument('--tail', '-t', type=int, default=50,
                       help='마지막 N줄 출력 (기본값: 50)')
    parser.add_argument('--follow', action='store_true',
                       help='실시간 로그 모니터링')
    parser.add_argument('--level', choices=['INFO', 'WARNING', 'ERROR'],
                       help='로그 레벨 필터')
    parser.add_argument('--date', help='날짜 필터 (YYYY-MM-DD 형식)')
    parser.add_argument('--keyword', '-k', help='키워드 필터')
    parser.add_argument('--stats', action='store_true',
                       help='로그 파일 통계 출력')
    parser.add_argument('--clear', action='store_true',
                       help='오래된 로그 정리 (백업 후)')
    
    args = parser.parse_args()
    
    log_file = args.file
    
    # 로그 파일이 현재 디렉토리에 없으면 절대 경로 확인
    if not os.path.exists(log_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(script_dir, args.file)
    
    if args.stats:
        show_log_stats(log_file)
        return
        
    if args.clear:
        confirm = input("로그 파일을 정리하시겠습니까? (백업 후 삭제) [y/N]: ")
        if confirm.lower() in ['y', 'yes']:
            clear_old_logs(log_file)
        return
        
    if args.follow:
        follow_log(log_file)
        return
        
    # 필터링 또는 tail 출력
    if args.level or args.date or args.keyword:
        lines = filter_logs(log_file, args.level, args.date, args.keyword)
        print(f"📋 필터 결과: {len(lines)}개 라인")
        for line in lines[-args.tail:]:
            print(line)
    else:
        lines = tail_log(log_file, args.tail)
        print(f"📋 마지막 {len(lines)}개 라인:")
        for line in lines:
            print(line.rstrip())

if __name__ == "__main__":
    main()
