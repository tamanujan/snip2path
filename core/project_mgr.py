import os
import json
import subprocess
from pathlib import Path
from PIL import Image

class ProjectManager:
    def __init__(self):
        # 設定ファイルはユーザーのホームディレクトリに隠しファイルで保存
        self.config_path = Path(os.path.expanduser("~/.snip2path_config.json"))
        self.master_img_path = self._load_master_path()

    def _load_master_path(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    path = data.get("master_path")
                    return Path(path) if path else None
            except:
                return None
        return None

    def save_master_path(self, path):
        # フォルダが指定されたら、その中に latest.png という名前で固定
        self.master_img_path = Path(path) / "latest.png"
        self.master_img_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 初回のダミー画像作成
        if not self.master_img_path.exists():
            img = Image.new('RGB', (1, 1), color='white')
            img.save(self.master_img_path)
            
        with open(self.config_path, "w") as f:
            json.dump({"master_path": str(self.master_img_path)}, f)

    def link_to_project(self, project_path):
        if not self.master_img_path:
            return False, "Master path not set."
        
        target_dir = Path(project_path) / ".snips"
        target_dir.mkdir(exist_ok=True)
        link_path = target_dir / "latest.png"

        # 既存のファイルがあれば削除して作り直す
        if link_path.exists() or link_path.is_symlink():
            try:
                if link_path.is_dir() and not link_path.is_symlink():
                     import shutil
                     shutil.rmtree(link_path)
                else:
                    link_path.unlink()
            except:
                pass

        try:
            # Windowsのmklinkコマンドを呼び出す
            # /H はハードリンク（これなら管理者権限なしでも動きやすい）
            subprocess.run(['cmd', '/c', 'mklink', '/H', str(link_path), str(self.master_img_path)], check=True)
            return True, f"Linked to {link_path}"
        except Exception as e:
            return False, f"Link error: {e}"

    def get_latest_path(self):
        return str(self.master_img_path)

    def get_relative_path(self):
        return "./.snips/latest.png"
