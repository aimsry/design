"""图加载器"""
import json
import os
from typing import Dict, Any
from pathlib import Path

class GraphLoader:
    """图定义加载器"""

    def __init__(self, graphs_dir: str = "graphs"):
        self.graphs_dir = Path(graphs_dir)
        self.graphs_dir.mkdir(exist_ok=True)
        print(f"[INFO] 图存储目录: {self.graphs_dir.absolute()}")

    def save_graph_definition(self, graph_id: str, definition: Dict[str, Any]) -> str:
        """保存图定义到文件"""
        file_path = self.graphs_dir / f"{graph_id}.json"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(definition, f, ensure_ascii=False, indent=2)
            print(f"[INFO] 图定义已保存: {file_path}")
            return str(file_path)
        except Exception as e:
            print(f"[ERROR] 保存图定义失败: {e}")
            raise

    def load_graph_definition(self, graph_id: str) -> Dict[str, Any]:
        """从文件加载图定义"""
        file_path = self.graphs_dir / f"{graph_id}.json"
        if not file_path.exists():
            available = self.list_available_graphs()
            raise FileNotFoundError(f"图定义文件不存在: {file_path}. 可用图: {available}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                definition = json.load(f)
            print(f"[INFO] 图定义已加载: {graph_id}")
            return definition
        except Exception as e:
            print(f"[ERROR] 加载图定义失败: {e}")
            raise

    def list_available_graphs(self) -> list:
        """列出所有可用的图"""
        try:
            json_files = list(self.graphs_dir.glob("*.json"))
            graph_names = [f.stem for f in json_files]
            print(f"[INFO] 可用图列表: {graph_names}")
            return graph_names
        except Exception as e:
            print(f"[ERROR] 列出图失败: {e}")
            return []

    def delete_graph_definition(self, graph_id: str) -> bool:
        """删除图定义文件"""
        file_path = self.graphs_dir / f"{graph_id}.json"
        try:
            if file_path.exists():
                file_path.unlink()
                print(f"[INFO] 图定义已删除: {graph_id}")
                return True
            else:
                print(f"[WARN] 图定义不存在: {graph_id}")
                return False
        except Exception as e:
            print(f"[ERROR] 删除图定义失败: {e}")
            return False

    def graph_exists(self, graph_id: str) -> bool:
        """检查图是否存在"""
        file_path = self.graphs_dir / f"{graph_id}.json"
        return file_path.exists()
