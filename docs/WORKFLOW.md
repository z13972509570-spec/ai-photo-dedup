# 工作流程

## 开发流程

```
1. Fork 项目
2. 创建分支: git checkout -b feature/xxx
3. 开发 + 测试
4. 提交: git commit -m "feat: add xxx"
5. 推送: git push origin feature/xxx
6. 创建 Pull Request
7. 代码审查
8. 合并
```

## 分支策略

| 分支 | 用途 | 保护 |
|------|------|------|
| main | 生产代码 | ✅ |
| develop | 开发代码 | ✅ |
| feature/* | 新功能 | ❌ |
| bugfix/* | Bug 修复 | ❌ |

## 提交规范

```
feat: 新功能
fix: Bug 修复
docs: 文档
refactor: 重构
test: 测试
chore: 构建/工具
```

## 发布流程

1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建 Release
4. 合并到 main
