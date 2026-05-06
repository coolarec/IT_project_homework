# 吴锦皓邮箱切换演示

本分支用于演示在 Git 提交时切换提交身份邮箱。

演示邮箱：
- `sdutwujinhao@gmail.com`

单次提交示例：

```bash
GIT_AUTHOR_NAME="吴锦皓" \
GIT_AUTHOR_EMAIL="sdutwujinhao@gmail.com" \
GIT_COMMITTER_NAME="吴锦皓" \
GIT_COMMITTER_EMAIL="sdutwujinhao@gmail.com" \
git commit -m "docs: add wujinhao email demo"
```
