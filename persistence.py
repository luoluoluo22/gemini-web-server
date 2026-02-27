import os
import sqlite3
import json
import shutil
from pathlib import Path
from datetime import datetime

class PersistenceManager:
    """
    带云端同步功能的持久化管理器
    支持本地 SQLite 存储，并可选择同步到 Hugging Face Dataset
    """
    def __init__(self, db_path="data.sqlite", dataset_repo=None, hf_token=None):
        self.db_path = db_path
        self.dataset_repo = dataset_repo or os.getenv("DATASET_REPO_ID")
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        
        # 初始化数据库表
        self._init_db()
        
        # 如果在 HF 环境且配置了仓库，则尝试恢复数据
        if self.dataset_repo and self.hf_token:
            self.restore_from_cloud()

    def _init_db(self):
        """初始化数据库结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def get_all_config(self, default_config):
        """从数据库加载所有配置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM settings')
        rows = cursor.fetchall()
        conn.close()
        
        config = default_config.copy()
        for key, value in rows:
            try:
                # 尝试解析 JSON（以支持列表和字典）
                config[key] = json.loads(value)
            except:
                config[key] = value
        return config

    def save_config(self, config_dict):
        """保存配置到数据库并同步到云端"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for key, value in config_dict.items():
            val_str = json.dumps(value, ensure_ascii=False)
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, val_str, now))
            
        conn.commit()
        conn.close()
        
        # 触发云端备份
        if self.dataset_repo and self.hf_token:
            self.save_to_cloud()

    def restore_from_cloud(self):
        """从 Hugging Face Dataset 下载数据库"""
        try:
            from huggingface_hub import hf_hub_download
            print(f"[*] 正在从云端 Dataset [{self.dataset_repo}] 恢复数据库...")
            
            downloaded_path = hf_hub_download(
                repo_id=self.dataset_repo,
                repo_type="dataset",
                filename=self.db_path,
                token=self.hf_token,
                force_download=True
            )
            
            shutil.copy(downloaded_path, self.db_path)
            print("✅ 数据库恢复成功")
        except Exception as e:
            print(f"⚠️ 云端恢复跳过或失败: {e}")

    def save_to_cloud(self):
        """将数据库上传到 Hugging Face Dataset"""
        try:
            from huggingface_hub import HfApi
            if not self.hf_token:
                print("❌ 云端备份失败: 未检测到 HF_TOKEN 环境变量")
                return
            
            api = HfApi(token=self.hf_token)
            print(f"[*] 正在备份数据库到云端: {self.db_path} -> {self.dataset_repo} ...")
            
            api.upload_file(
                path_or_fileobj=self.db_path,
                path_in_repo=self.db_path,
                repo_id=self.dataset_repo,
                repo_type="dataset",
                commit_message=f"Persist Gemini db at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            print("✅ 云端备份成功！文件已推送到 Dataset。")
        except Exception as e:
            print(f"❌ 云端备份失败，详细错误: {str(e)}")
