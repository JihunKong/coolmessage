import pystray
import threading
from PIL import Image, ImageDraw
import sys
import os

class SystemTrayApp:
    """시스템 트레이 앱"""
    
    def __init__(self, processor):
        self.processor = processor
        self.running = True
        self.icon = None
        
    def create_icon_image(self):
        """트레이 아이콘 이미지 생성"""
        # 간단한 아이콘 생성
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='blue')
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill='white')
        draw.text((20, 20), "CM", fill='blue')
        return image
    
    def quit_app(self, icon, item):
        """앱 종료"""
        self.running = False
        icon.stop()
        sys.exit(0)
    
    def show_status(self, icon, item):
        """상태 표시"""
        print("CoolMessenger가 백그라운드에서 실행 중입니다.")
    
    def run_tray(self):
        """시스템 트레이 실행"""
        menu = pystray.Menu(
            pystray.MenuItem("상태 확인", self.show_status),
            pystray.MenuItem("종료", self.quit_app)
        )
        
        self.icon = pystray.Icon(
            "CoolMessenger",
            self.create_icon_image(),
            "CoolMessenger - 백그라운드 실행 중",
            menu
        )
        
        self.icon.run()
