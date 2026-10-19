import io
p="build_site.py"; s=io.open(p,encoding="utf-8").read()
# 1) 修正按钮配色（变量名应为 --accent-a）
s=s.replace("  background: var(--accent);\n  border: 0;","  background: var(--accent-a);\n  border: 0;")
# 2) html/body 横向溢出兜底
s=s.replace("html { -webkit-text-size-adjust: 100%; }",
            "html { -webkit-text-size-adjust: 100%; overflow-x: hidden; }")
s=s.replace("  line-height: 1.55;\n}","  line-height: 1.55;\n  overflow-x: hidden;\n}")
# 3) 加大标题换行安全性
s=s.replace(".masthead h1 {\n  margin: 0 0 6px;\n  font-size: 30px;\n  line-height: 1.25;\n}",
            ".masthead h1 {\n  margin: 0 0 6px;\n  font-size: 30px;\n  line-height: 1.25;\n  overflow-wrap: anywhere;\n}")
# 4) favicon
s=s.replace('<link rel="stylesheet" href="style.css">',
            '<link rel="icon" href="favicon.png" type="image/png">\n<link rel="stylesheet" href="style.css">')
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
