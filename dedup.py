#!/usr/bin/env python3
"""
AI Photo Dedup — AI 智能清理重复照片
====================================

使用方法:
    python dedup.py scan ./photos          # 扫描并生成报告
    python dedup.py clean ./photos         # 清理重复文件
    python dedup.py clean ./photos --dry-run  # 预览清理操作
"""
import click
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from core import DedupEngine, PerceptualHasher, CLIPFeatureExtractor
from reports import HTMLReportGenerator
from utils import setup_logger, safe_delete, is_valid_image
from config import settings

console = Console()
logger = setup_logger(settings.LOG_LEVEL)


@click.group()
@click.version_option('1.0.0')
def cli():
    """🤖 AI 智能清理重复照片工具"""
    pass


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--output', '-o', default='dedup_report.html', help='报告输出文件名')
@click.option('--use-clip/--no-clip', default=True, help='是否使用 CLIP 深度验证')
def scan(directory: str, output: str, use_clip: bool):
    """扫描目录并生成去重报告"""
    dir_path = Path(directory).resolve()
    console.print(f"\n[bold blue]📁 扫描目录:[/] {dir_path}\n")

    engine = DedupEngine()

    # 扫描文件
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("正在扫描图片文件...", total=None)
        files = engine.scan_directory(dir_path)

        # 过滤有效图片
        valid_files = [f for f in files if is_valid_image(f)]

        progress.update(task, description=f"发现 {len(valid_files)} 张有效图片")

    if not valid_files:
        console.print("[yellow]未找到有效的图片文件[/]")
        return

    # 分析去重
    console.print("\n[bold]🔍 开始分析图片相似度...[/]")
    groups = engine.analyze(valid_files, use_clip=use_clip)

    if not groups:
        console.print("\n[green]✅ 未发现重复图片！[/]")
        return

    # 生成报告
    report_data = engine.generate_report_data(groups, len(valid_files))

    # 控制台输出摘要
    table = Table(title="📊 分析结果")
    table.add_column("指标", style="cyan")
    table.add_column("数值", style="green")
    table.add_row("扫描文件数", str(report_data['total_files']))
    table.add_row("重复组数", str(report_data['duplicate_groups']))
    table.add_row("重复文件数", str(report_data['total_duplicates']))
    table.add_row("可释放空间", f"{report_data['space_to_save_mb']:.1f} MB")
    console.print(table)

    # 生成 HTML 报告
    generator = HTMLReportGenerator()
    report_path = generator.generate(report_data, output)
    console.print(f"\n[green]✅ 报告已生成:[/] {report_path}")


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--dry-run', is_flag=True, help='预览模式，不实际删除')
@click.option('--confirm/--no-confirm', default=True, help='删除前确认')
@click.option('--backup-dir', type=click.Path(), default='./backup', help='备份目录')
def clean(directory: str, dry_run: bool, confirm: bool, backup_dir: str):
    """清理重复照片（保留质量最高的版本）"""
    dir_path = Path(directory).resolve()
    backup = Path(backup_dir).resolve()

    console.print(f"\n[bold blue]🧹 清理目录:[/] {dir_path}")
    if dry_run:
        console.print("[yellow]⚠️  预览模式 - 不会实际删除文件[/]\n")

    engine = DedupEngine()
    files = engine.scan_directory(dir_path)
    groups = engine.analyze(files, use_clip=True)

    if not groups:
        console.print("[green]✅ 未发现重复图片，无需清理[/]")
        return

    # 统计
    total_to_delete = 0
    total_space = 0

    for group in groups:
        best = group.get_best_quality_file()
        for f in group.files:
            if f != best:
                total_to_delete += 1
                total_space += f.stat().st_size

    console.print(f"[yellow]将删除 {total_to_delete} 个文件，释放 {total_space / (1024*1024):.1f} MB[/]")

    if confirm and not dry_run:
        if not click.confirm("\n确认执行删除？"):
            console.print("[red]已取消[/]")
            return

    # 执行清理
    deleted = 0
    for group in groups:
        best = group.get_best_quality_file()
        for f in group.files:
            if f != best:
                if dry_run:
                    console.print(f"[dim]  预览删除: {f.name}[/]")
                else:
                    if safe_delete(f, backup):
                        deleted += 1

    if dry_run:
        console.print(f"\n[yellow]预览完成: 将删除 {total_to_delete} 个文件[/]")
    else:
        console.print(f"\n[green]✅ 清理完成: 已删除 {deleted} 个文件[/]")
        console.print(f"[dim]备份位置: {backup}[/]")


if __name__ == '__main__':
    cli()
