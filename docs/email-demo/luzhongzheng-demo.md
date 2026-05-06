# 路忠政邮箱切换演示

本分支用于演示在 Git 提交时切换提交身份邮箱。

演示邮箱：
- `1549430901@qq.com`

单次提交示例：

```bash
GIT_AUTHOR_NAME="路忠政" \
GIT_AUTHOR_EMAIL="1549430901@qq.com" \
GIT_COMMITTER_NAME="路忠政" \
GIT_COMMITTER_EMAIL="1549430901@qq.com" \
git commit -m "docs: add luzhongzheng email demo"
```
