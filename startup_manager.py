import os
import sys
import winreg
import subprocess
from pathlib import Path

class WindowsStartupManager:
    """윈도우 시작 프로그램 관리"""
    
    def __init__(self, app_name="CoolMessenger", script_path=None):
        self.app_name = app_name
        self.script_path = script_path or os.path.abspath(sys.argv[0])
        self.registry_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    
    def add_to_startup(self):
        """시작 프로그램에 추가"""
        try:
            # Python 실행 파일 경로 찾기
            python_exe = sys.executable
            script_path = os.path.abspath(self.script_path)
            
            # 실행 명령어 생성
            command = f'"{python_exe}" "{script_path}"'
            
            # 레지스트리에 등록
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_key, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, command)
            
            print(f"[성공] {self.app_name}이(가) 시작 프로그램에 추가되었습니다.")
            print(f"   실행 경로: {command}")
            return True
            
        except Exception as e:
            print(f"[실패] 시작 프로그램 추가 실패: {e}")
            return False
    
    def remove_from_startup(self):
        """시작 프로그램에서 제거"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_key, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, self.app_name)
            
            print(f"[성공] {self.app_name}이(가) 시작 프로그램에서 제거되었습니다.")
            return True
            
        except FileNotFoundError:
            print(f"[정보] {self.app_name}이(가) 시작 프로그램에 등록되어 있지 않습니다.")
            return True
        except Exception as e:
            print(f"[실패] 시작 프로그램 제거 실패: {e}")
            return False
    
    def is_in_startup(self):
        """시작 프로그램에 등록되어 있는지 확인"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_key, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, self.app_name)
                return True
        except FileNotFoundError:
            return False
        except Exception:
            return False
    
    def create_task_scheduler_entry(self):
        """작업 스케줄러를 사용한 시작 프로그램 등록 (대안 방법)"""
        try:
            python_exe = sys.executable
            script_path = os.path.abspath(self.script_path)
            
            # 작업 스케줄러 XML 생성
            task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>CoolMessenger 자동 실행</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions>
    <Exec>
      <Command>"{python_exe}"</Command>
      <Arguments>"{script_path}"</Arguments>
    </Exec>
  </Actions>
</Task>"""
            
            # 임시 XML 파일 생성
            temp_xml = os.path.join(os.path.dirname(script_path), "coolmessenger_task.xml")
            with open(temp_xml, 'w', encoding='utf-16') as f:
                f.write(task_xml)
            
            # 작업 스케줄러에 등록
            cmd = f'schtasks /create /tn "{self.app_name}" /xml "{temp_xml}" /f'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # 임시 파일 삭제
            os.remove(temp_xml)
            
            if result.returncode == 0:
                print(f"[성공] 작업 스케줄러에 {self.app_name} 등록 완료")
                return True
            else:
                print(f"[실패] 작업 스케줄러 등록 실패: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[실패] 작업 스케줄러 등록 실패: {e}")
            return False

if __name__ == "__main__":
    # 테스트
    manager = WindowsStartupManager("CoolMessenger", "coolmessenger_auto.py")
    
    print("현재 상태:", "등록됨" if manager.is_in_startup() else "등록되지 않음")
    
    choice = input("1: 시작프로그램 추가, 2: 제거, 3: 작업스케줄러 등록: ")
    
    if choice == "1":
        manager.add_to_startup()
    elif choice == "2":
        manager.remove_from_startup()
    elif choice == "3":
        manager.create_task_scheduler_entry()
