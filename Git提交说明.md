# Git提交说明

## 快速提交

### 方法1：使用批处理脚本（推荐）

**双击运行** `提交到GitHub.bat`

脚本会自动完成：
1. 初始化Git仓库（如果需要）
2. 添加所有文件
3. 提交更改
4. 添加远程仓库
5. 推送到GitHub

### 方法2：手动提交

```bash
# 1. 初始化仓库（如果还没有）
git init

# 2. 添加所有文件
git add .

# 3. 提交更改
git commit -m "初始提交：小灰熊歌词格式转换器"

# 4. 添加远程仓库
git remote add origin https://github.com/wyh-alt/Lyrics_conversion_KBuilder.git

# 5. 推送到GitHub
git branch -M main
git push -u origin main
```

---

## 首次提交前准备

### 1. 配置Git用户信息（如果还没配置）

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2. 配置GitHub认证

**方式1：使用HTTPS + Personal Access Token**

1. 在GitHub创建Personal Access Token
2. 推送时使用token作为密码

**方式2：使用SSH密钥**

```bash
# 生成SSH密钥
ssh-keygen -t ed25519 -C "your.email@example.com"

# 将公钥添加到GitHub
# 复制 ~/.ssh/id_ed25519.pub 内容到GitHub Settings > SSH Keys
```

然后修改远程地址：
```bash
git remote set-url origin git@github.com:wyh-alt/Lyrics_conversion_KBuilder.git
```

---

## 提交的文件

### 包含的文件

- ✅ `lyric_converter.py` - 主程序
- ✅ `requirements.txt` - 依赖列表
- ✅ `README.md` - 使用说明
- ✅ `打包说明.md` - 打包文档
- ✅ `编码说明.md` - 编码说明
- ✅ `韩文字符处理说明.md` - 韩文处理说明
- ✅ `build_exe.bat` - 打包脚本
- ✅ `快速打包.bat` - 快速打包脚本
- ✅ `.gitignore` - Git忽略配置
- ✅ 其他文档文件

### 排除的文件（.gitignore）

- ❌ `__pycache__/` - Python缓存
- ❌ `build/` - 构建目录
- ❌ `dist/` - 打包输出
- ❌ `*.spec` - PyInstaller配置
- ❌ `测试_*.txt` - 测试文件
- ❌ `.idea/`, `.vscode/` - IDE配置

---

## 后续更新

### 日常提交流程

```bash
# 1. 查看更改
git status

# 2. 添加更改的文件
git add .

# 3. 提交
git commit -m "更新说明：描述本次更改内容"

# 4. 推送
git push
```

### 提交信息规范

建议使用清晰的提交信息：

```
功能更新：添加XX功能
修复：修复XX问题
优化：优化XX性能
文档：更新XX文档
```

---

## 常见问题

### Q1：推送失败，提示认证错误

**解决方案**：
1. 使用Personal Access Token替代密码
2. 或配置SSH密钥
3. 或使用GitHub Desktop客户端

### Q2：推送失败，提示权限不足

**解决方案**：
1. 确认GitHub仓库权限
2. 确认远程地址正确
3. 确认已登录GitHub账户

### Q3：如何查看远程仓库

```bash
git remote -v
```

### Q4：如何修改远程地址

```bash
git remote set-url origin https://github.com/wyh-alt/Lyrics_conversion_KBuilder.git
```

---

## GitHub仓库信息

- **仓库地址**：https://github.com/wyh-alt/Lyrics_conversion_KBuilder.git
- **仓库名称**：Lyrics_conversion_KBuilder
- **所有者**：wyh-alt

---

## 注意事项

1. **不要提交敏感信息**
   - API密钥
   - 密码
   - 个人隐私信息

2. **不要提交大文件**
   - 打包后的exe文件（建议通过Release发布）
   - 大型测试文件

3. **保持提交信息清晰**
   - 描述做了什么更改
   - 为什么做这些更改

---

**祝提交顺利！** 🚀

