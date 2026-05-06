# 崔立栋邮箱切换演示

本分支用于演示在 Git 提交时切换提交身份邮箱。

演示邮箱：
- `coolarec@qq.com`

单次提交示例：

```bash
GIT_AUTHOR_NAME="崔立栋" \
GIT_AUTHOR_EMAIL="coolarec@qq.com" \
GIT_COMMITTER_NAME="崔立栋" \
GIT_COMMITTER_EMAIL="coolarec@qq.com" \
git commit -m "docs: add cuilidong email demo"
```
