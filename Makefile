.PHONY: install test clean run

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info/

run:
	python dedup.py scan ./photos
PYEOF

echo "✅ 测试和 Makefile 已生成"
echo ""
echo "=== 项目结构 ==="
find . -type f | grep -v __pycache__ | sort