from PIL import ImageGrab
import pyperclip

class SnipCapturer:
    def __init__(self, project_mgr):
        self.project_mgr = project_mgr

    def capture_and_save(self, rect):
        save_path = self.project_mgr.get_latest_path()
        if not save_path: return False, "No project."
        # Windows側の座標系で処理
        bbox = (rect.x(), rect.y(), rect.x() + rect.width(), rect.y() + rect.height())
        try:
            screenshot = ImageGrab.grab(bbox=bbox, all_screens=True)
            screenshot.save(save_path, "PNG")
            pyperclip.copy(self.project_mgr.get_relative_path())
            return True, "Captured."
        except Exception as e:
            return False, str(e)
