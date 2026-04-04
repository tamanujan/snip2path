import os
import json
import subprocess
import shutil
from pathlib import Path
from PIL import Image

class ProjectManager:
    def __init__(self):
        # 設定ファイルはユーザーのホームディレクトリに隠しファイルで保存
        self.config_path = Path(os.path.expanduser("~/.snip2path_config.json"))
        self.master_img_path = self._load_master_path()

    def _load_master_path(self):
        """設定ファイルからマスターパスを復元"""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    path = data.get("master_path")
                    return Path(path) if path else None
            except:
                return None
        return None

    def save_master_path(self, folder_path):
        """マスター画像の保存先を設定し、設定ファイルに書き込む"""
        self.master_img_path = Path(folder_path) / "latest.png"
        self.master_img_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 初回のダミー画像作成
        if not self.master_img_path.exists():
            img = Image.new('RGB', (1, 1), color='white')
            img.save(self.master_img_path)
            
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump({"master_path": str(self.master_img_path)}, f)

    def link_to_project(self, project_root):
        """プロジェクト内に .snips フォルダを作成し、ハードリンクを張る"""
        if not self.master_img_path:
            return False, "Master path not set."
        
        target_dir = Path(project_root) / ".snips"
        target_dir.mkdir(exist_ok=True)
        link_path = target_dir / "latest.png"

        # --- .gitignore 生成処理を削除しました ---

        # 既存のリンクがあれば削除
        if link_path.exists() or link_path.is_symlink():
            try:
                if link_path.is_dir() and not link_path.is_symlink():
                     shutil.rmtree(link_path)
                else:
                    link_path.unlink()
            except:
                pass

        # ハードリンクの作成
        try:
            subprocess.run(['cmd', '/c', 'mklink', '/H', str(link_path), str(self.master_img_path)], 
                           check=True, capture_output=True)
            return True, f"Linked to {link_path}"
        except Exception as e:
            return False, f"Link error: {e}"

    def get_latest_path(self):
        return str(self.master_img_path) if self.master_img_path else ""

    def get_relative_path(self):
        return "./.snips/latest.png"