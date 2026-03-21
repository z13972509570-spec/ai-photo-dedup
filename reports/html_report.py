"""HTML 交互式报告生成器"""
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import json
from jinja2 import Template


class HTMLReportGenerator:
    """生成交互式 HTML 去重报告"""

    TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Photo Dedup Report - {{ date }}</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               background: #f5f5f5; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #333; margin-bottom: 10px; }
        .summary { background: white; padding: 20px; border-radius: 10px; 
                   box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-top: 20px; }
        .stat { text-align: center; }
        .stat-value { font-size: 2em; font-weight: bold; color: #2563eb; }
        .stat-label { color: #666; margin-top: 5px; }
        .group { background: white; border-radius: 10px; padding: 20px; 
                 margin-bottom: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .group-header { display: flex; justify-content: space-between; align-items: center; 
                        margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #eee; }
        .group-title { font-size: 1.2em; font-weight: 600; }
        .score { padding: 5px 12px; border-radius: 20px; font-size: 0.9em; }
        .score-high { background: #dbeafe; color: #1e40af; }
        .score-medium { background: #fef3c7; color: #92400e; }
        .files { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; }
        .file-card { border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; }
        .file-card.best { border-color: #22c55e; background: #f0fdf4; }
        .file-name { font-weight: 500; margin-bottom: 5px; word-break: break-all; }
        .file-size { color: #666; font-size: 0.9em; }
        .best-badge { display: inline-block; background: #22c55e; color: white; 
                      padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-left: 8px; }
        .actions { margin-top: 15px; display: flex; gap: 10px; }
        .btn { padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9em; }
        .btn-delete { background: #ef4444; color: white; }
        .btn-keep { background: #22c55e; color: white; }
        footer { text-align: center; margin-top: 40px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI Photo Dedup Report</h1>
        <p style="color: #666; margin-bottom: 20px;">生成时间: {{ date }}</p>

        <div class="summary">
            <h2>📊 分析摘要</h2>
            <div class="summary-grid">
                <div class="stat">
                    <div class="stat-value">{{ total_files }}</div>
                    <div class="stat-label">扫描文件</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{{ duplicate_groups }}</div>
                    <div class="stat-label">重复组</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{{ total_duplicates }}</div>
                    <div class="stat-label">重复文件</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{{ space_to_save }}</div>
                    <div class="stat-label">可释放空间</div>
                </div>
            </div>
        </div>

        <h2 style="margin-bottom: 15px;">📁 重复文件组</h2>
        {% for group in groups %}
        <div class="group">
            <div class="group-header">
                <span class="group-title">组 {{ loop.index }}</span>
                <span class="score {% if group.hash_score > 0.95 %}score-high{% else %}score-medium{% endif %}">
                    相似度: {{ "%.1f"|format(group.hash_score * 100) }}%
                </span>
            </div>
            <div class="files">
                {% for file in group.files %}
                <div class="file-card {% if file.is_best %}best{% endif %}">
                    <div class="file-name">
                        {{ file.name }}
                        {% if file.is_best %}<span class="best-badge">保留</span>{% endif %}
                    </div>
                    <div class="file-size">{{ file.size }}</div>
                </div>
                {% endfor %}
            </div>
            <div class="actions">
                <button class="btn btn-delete" onclick="deleteGroup({{ loop.index0 }})">删除其他，保留最佳</button>
                <button class="btn btn-keep" onclick="keepAll({{ loop.index0 }})">全部保留</button>
            </div>
        </div>
        {% endfor %}

        <footer>
            <p>🤖 AI Photo Dedup — AI 智能清理重复照片</p>
        </footer>
    </div>

    <script>
        const reportData = {{ report_json }};

        function deleteGroup(groupIndex) {
            const group = reportData.groups[groupIndex];
            const bestFile = group.files.find(f => f === group.best_file);
            if (confirm('确定删除此组中除最佳文件外的所有文件吗？')) {
                console.log('Delete group:', groupIndex);
                alert('删除功能需要使用 CLI: python dedup.py clean --confirm');
            }
        }

        function keepAll(groupIndex) {
            console.log('Keep all in group:', groupIndex);
        }
    </script>
</body>
</html>
'''

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path('./reports/output')
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        report_data: Dict,
        output_file: str = 'dedup_report.html'
    ) -> Path:
        """生成 HTML 报告"""
        # 格式化数据
        from utils.file_utils import format_size
        groups = []
        for g in report_data['groups']:
            files = []
            best_file = g.get('best_file', g['files'][0])
            for f in g['files']:
                try:
                    size = format_size(g['sizes'][g['files'].index(f)])
                except:
                    size = 'Unknown'
                files.append({
                    'name': Path(f).name,
                    'path': f,
                    'size': size,
                    'is_best': f == best_file
                })
            groups.append({
                'files': files,
                'hash_score': g.get('hash_score', 0),
                'clip_score': g.get('clip_score', 0)
            })

        html_data = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_files': report_data['total_files'],
            'duplicate_groups': report_data['duplicate_groups'],
            'total_duplicates': report_data['total_duplicates'],
            'space_to_save': f"{report_data['space_to_save_mb']:.1f} MB",
            'groups': groups,
            'report_json': json.dumps(report_data)
        }

        template = Template(self.TEMPLATE)
        html = template.render(**html_data)

        output_path = self.output_dir / output_file
        output_path.write_text(html, encoding='utf-8')
        return output_path
