# 最小发布闭环

当前 site.zip 为已验收公开版；不要从旧源码全量构建覆盖。
1. 从上次成功发布的 commit 解开唯一 site.zip，修改独立副本，不改正式站。
2. 更新 site.zip，并更新 release.json 的版本、baseline_commit、改动说明、归档 SHA256、逐文件 SHA256 和文件数。不要留下 site-old.zip 等额外包。
3. 在独立分支运行 python3 scripts/validate_site.py 与 python3 scripts/test_validate_site.py；审查实际改动、来源许可、私人信息及资源路径。
4. 经人工审阅后合并 main 才可部署；候选分支和 PR 只校验，不部署。
5. 部署后匿名验证首页、第五套、练声曲深链刷新、小节切换和试听状态；HTTP 成功不等于音乐正确或真机有声。
6. 失败时恢复上次已验收的 site.zip 和匹配 release.json，重新提交部署。不要强推或删除历史。

自动校验只保证归档/文件清单一致、ZIP 路径与文件类型安全、JSON可解析和必要入口及署名存在。它不是恶意代码扫描、完整资源引用检查、音乐审定或浏览器验收。SHA 清单是完整性记录，不是可信签名。

当前工作流仅 main 拥有部署路径；工作流本身或权限更改仍需单独审阅。
