import json
import subprocess
import shutil
from pathlib import Path
from PIL import Image

LEGACY_CONFIG_PATH = Path.home() / ".snip2path_config.json"


class ProjectManager:
    def __init__(self):
        self.app_dir = Path.home() / ".snip2path"
        self.master_img_path = self.app_dir / "latest.png"
        self._ensure_master_image()

    def _ensure_master_image(self):
        self.app_dir.mkdir(parents=True, exist_ok=True)
        if not self.master_img_path.exists():
            if LEGACY_CONFIG_PATH.exists():
                try:
                    with open(LEGACY_CONFIG_PATH, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    old = data.get("master_path")
                    if old:
                        old_path = Path(old)
                        if old_path.is_file():
                            shutil.copy2(old_path, self.master_img_path)
                except Exception:
                    pass
            if not self.master_img_path.exists():
                img = Image.new("RGB", (1, 1), color="white")
                img.save(self.master_img_path)
        self._remove_legacy_config()

    def _remove_legacy_config(self):
        if LEGACY_CONFIG_PATH.exists():
            try:
                LEGACY_CONFIG_PATH.unlink()
            except Exception:
                pass

    def link_to_project(self, project_root):
        """プロジェクト内に .snips フォルダを作成し、ハードリンクを張る"""
        target_dir = Path(project_root) / ".snips"
        target_dir.mkdir(exist_ok=True)
        link_path = target_dir / "latest.png"

        if link_path.exists() or link_path.is_symlink():
            try:
                if link_path.is_dir() and not link_path.is_symlink():
                    shutil.rmtree(link_path)
                else:
                    link_path.unlink()
            except Exception:
                pass

        try:
            subprocess.run(
                ["cmd", "/c", "mklink", "/H", str(link_path), str(self.master_img_path)],
                check=True,
                capture_output=True,
            )
            return True, f"Linked to {link_path}"
        except Exception as e:
            return False, f"Link error: {e}"

    def get_latest_path(self):
        return str(self.master_img_path)

    def get_relative_path(self):
        return "./.snips/latest.png"
