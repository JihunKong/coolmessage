import sqlite3
import os
import time
import json
from datetime import datetime, timedelta
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from openai import OpenAI
import pickle
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CoolMessengerProcessor:
    def __init__(self, db_path, openai_api_key):
        self.db_path = db_path
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.calendar_service = None
        self.tasks_service = None
        self.last_message_key = self.get_last_message_key()
        
        # Google API 설정
        self.setup_google_apis()
    
    def setup_google_apis(self):
        """Google Calendar와 Tasks API 설정"""
        # 민감하지 않은 범위 사용 (검증 불필요)
        SCOPES = [
            'https://www.googleapis.com/auth/calendar.events',  # 이벤트만 관리
            'https://www.googleapis.com/auth/tasks.readonly'    # 읽기 전용으로 시작
        ]
        
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                
                print("브라우저에서 Google 로그인을 완료한 후,")
                print("주소창의 전체 URL을 복사해서 아래에 붙여넣으세요:")
                print("(http://localhost:포트번호/?state=...&code=...&scope=... 형태)")
                
                auth_url, _ = flow.authorization_url(prompt='consent')
                print(f"\n인증 URL: {auth_url}\n")
                
                # 사용자로부터 URL 입력받기
                full_url = input("전체 URL 입력: ").strip()
                
                # URL에서 code 파라미터 추출
                if 'code=' in full_url:
                    code_start = full_url.find('code=') + 5
                    code_end = full_url.find('&', code_start)
                    if code_end == -1:
                        auth_code = full_url[code_start:]
                    else:
                        auth_code = full_url[code_start:code_end]
                    
                    flow.fetch_token(code=auth_code)
                    creds = flow.credentials
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.calendar_service = build('calendar', 'v3', credentials=creds)
        self.tasks_service = build('tasks', 'v1', credentials=creds)
    
    def get_last_message_key(self):
        """마지막으로 처리한 메시지 키 가져오기"""
        try:
            with open('last_processed.txt', 'r') as f:
                return int(f.read().strip())
        except:
            return 0
    
    def save_last_message_key(self, message_key):
        """마지막으로 처리한 메시지 키 저장"""
        with open('last_processed.txt', 'w') as f:
            f.write(str(message_key))
    
    def get_new_messages(self):
        """새로운 메시지들 가져오기"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 새로운 메시지 조회 (MessageKey가 마지막 처리된 것보다 큰 것들)
            # 삭제되지 않은 메시지만 가져오기 (DeletedDate가 NULL)
            query = """
            SELECT MessageKey, MessageBody, Title, Sender, SenderKey, 
                   MessageType, ReceiveDate, MessageText, MemoID, 
                   ReferenceList, CCList, FilePath, IsUnRead
            FROM tbl_recv 
            WHERE MessageKey > ? AND DeletedDate IS NULL
            ORDER BY MessageKey ASC
            """
            
            cursor.execute(query, (self.last_message_key,))
            messages = cursor.fetchall()
            conn.close()
            
            return messages
            
        except Exception as e:
            print(f"데이터베이스 오류: {e}")
            return []
    
    def analyze_message_with_ai(self, message_text, sender, title):
        """OpenAI를 사용하여 메시지 분석"""
        prompt = f"""
        다음은 한국 학교에서 온 메시지입니다. 이 메시지에서 일정이나 할일을 추출해주세요.

        발신자: {sender}
        제목: {title}
        내용: {message_text}

        다음 중 하나로 분류하고 반드시 JSON 형식으로만 응답해주세요. 다른 설명은 추가하지 마세요.

        JSON 형식:
        {{
            "type": "calendar|todo|info",
            "priority": "high|medium|low",
            "title": "간단한 제목",
            "description": "상세 설명",
            "date": "YYYY-MM-DD",
            "time": "HH:MM",
            "deadline": "YYYY-MM-DD",
            "category": "수업|회의|행사|과제|기타"
        }}

        규칙:
        1. 회의, 행사, 수업 등 특정 시간에 해야 할 일 = "calendar"
        2. 과제, 제출물, 준비사항, 회신 등 = "todo"  
        3. 단순 공지, 정보 전달 = "info"
        4. 날짜/시간이 없으면 null로 설정
        5. 반드시 유효한 JSON만 반환
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "당신은 JSON만 반환하는 AI입니다. 설명 없이 오직 JSON 형식으로만 응답하세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            print(f"🤖 AI 원본 응답: {result}")
            
            # JSON 파싱 시도
            try:
                parsed_result = json.loads(result)
                return parsed_result
            except json.JSONDecodeError:
                # JSON 파싱 실패시 텍스트에서 JSON 추출 시도
                json_start = result.find('{')
                json_end = result.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_text = result[json_start:json_end]
                    return json.loads(json_text)
                else:
                    raise ValueError("JSON 형식을 찾을 수 없음")
            
        except Exception as e:
            print(f"AI 분석 오류: {e}")
            print(f"응답 내용: {result if 'result' in locals() else 'N/A'}")
            
            # 오류 발생시 기본값 반환
            return {
                "type": "info",
                "priority": "medium",
                "title": title[:50] if title else "메시지",
                "description": message_text[:100] if message_text else "내용 없음",
                "date": None,
                "time": None,
                "deadline": None,
                "category": "기타"
            }
    
    def add_to_calendar(self, event_data):
        """Google Calendar에 일정 추가"""
        try:
            # 날짜/시간 처리
            start_datetime = f"{event_data['date']}T{event_data.get('time', '09:00')}:00+09:00"
            end_time = datetime.fromisoformat(start_datetime.replace('+09:00', '')) + timedelta(hours=1)
            end_datetime = end_time.strftime("%Y-%m-%dT%H:%M:%S+09:00")
            
            event = {
                'summary': event_data['title'],
                'description': event_data['description'],
                'start': {
                    'dateTime': start_datetime,
                    'timeZone': 'Asia/Seoul',
                },
                'end': {
                    'dateTime': end_datetime,
                    'timeZone': 'Asia/Seoul',
                },
                'colorId': '1' if event_data['priority'] == 'high' else '2'
            }
            
            event = self.calendar_service.events().insert(
                calendarId='primary', body=event).execute()
            print(f"캘린더 일정 추가됨: {event_data['title']}")
            
        except Exception as e:
            print(f"캘린더 추가 오류: {e}")
    
    def add_to_tasks(self, task_data):
        """Google Tasks에 할일 추가"""
        try:
            task = {
                'title': task_data['title'],
                'notes': task_data['description'],
            }
            
            if 'deadline' in task_data and task_data['deadline']:
                task['due'] = f"{task_data['deadline']}T00:00:00.000Z"
            
            result = self.tasks_service.tasks().insert(
                tasklist='@default', body=task).execute()
            print(f"할일 추가됨: {task_data['title']}")
            
        except Exception as e:
            print(f"할일 추가 오류: {e}")
    
    def process_new_messages(self):
        """새로운 메시지들 처리"""
        messages = self.get_new_messages()
        
        for message in messages:
            message_key, body, title, sender, sender_key, msg_type, receive_date, msg_text, memo_id, ref_list, cc_list, file_path, is_unread = message
            
            # 메시지 텍스트 결정 (MessageText가 있으면 우선 사용)
            content = msg_text if msg_text else body
            if not content:
                content = title  # 제목이라도 있으면 사용
            
            if not content:
                continue
            
            print(f"새 메시지 처리: {sender} - {title}")
            print(f"받은 날짜: {receive_date}")
            print(f"메시지 유형: {msg_type}")
            
            # AI로 메시지 분석
            analysis = self.analyze_message_with_ai(content, sender, title)
            
            if analysis and isinstance(analysis, dict):
                print(f"✅ AI 분석 결과: {analysis.get('type', 'unknown')} - {analysis.get('title', 'No Title')}")
                
                if analysis.get('type') == 'calendar' and analysis.get('date'):
                    self.add_to_calendar(analysis)
                elif analysis.get('type') == 'todo':
                    self.add_to_tasks(analysis)
                elif analysis.get('type') == 'info':
                    print(f"📋 정보성 메시지로 분류: {analysis.get('title', 'No Title')}")
                    
                # 중요한 메시지나 파일이 첨부된 경우 로그 남기기
                if file_path or analysis.get('priority') == 'high':
                    print(f"📎 첨부파일: {file_path}" if file_path else "⚠️ 중요 메시지")
            else:
                print(f"❌ AI 분석 실패 또는 잘못된 형식")
                print(f"분석 결과: {analysis}")
            
            print("-" * 50)  # 구분선
            
            # 처리된 메시지 키 업데이트
            self.last_message_key = message_key
            self.save_last_message_key(message_key)
            
            # API 제한을 위한 잠시 대기
            time.sleep(1)

class DatabaseWatcher(FileSystemEventHandler):
    """데이터베이스 파일 변경 감지"""
    def __init__(self, processor):
        self.processor = processor
    
    def on_modified(self, event):
        if event.src_path.endswith('.udb'):
            print("쿨메신저 데이터베이스 업데이트 감지!")
            time.sleep(2)  # 파일 쓰기 완료 대기
            self.processor.process_new_messages()

def main():
    # 설정
    DB_PATH = r"C:\Users\2학년교무부장\AppData\Local\CoolMessenger\Memo\your-coolmessenger-ID.udb"
    OPENAI_API_KEY = "your-openai-api-key"  # 실제 API 키로 교체
    
    # API 키 확인
    if OPENAI_API_KEY == "your-openai-api-key":
        print("❌ OpenAI API 키를 설정해주세요!")
        print("OPENAI_API_KEY 변수에 실제 API 키를 입력하세요.")
        return
    
    # 프로세서 초기화
    processor = CoolMessengerProcessor(DB_PATH, OPENAI_API_KEY)
    
    # 파일 변경 감지 설정
    event_handler = DatabaseWatcher(processor)
    observer = Observer()
    observer.schedule(event_handler, os.path.dirname(DB_PATH), recursive=False)
    
    # 프로그램 시작
    print("쿨메신저 AI 자동화 프로그램 시작...")
    
    # 기존 메시지 처리 (처음 실행시)
    processor.process_new_messages()
    
    # 파일 감시 시작
    observer.start()
    
    try:
        while True:
            time.sleep(60)  # 1분마다 체크
            processor.process_new_messages()
    except KeyboardInterrupt:
        observer.stop()
        print("프로그램 종료")
    
    observer.join()

if __name__ == "__main__":
    main()
