import io
p="build_site.py"; s=io.open(p,encoding="utf-8").read()
s=s.replace(".playall[hidden] { display: none; }",
""".playall[hidden] { display: none; }

/* 交互实验台入口卡片 */
.labcard { border-color: var(--accent-a); }
.labcard .badge { background: var(--accent-a); color: #08111a; }
.labcard .count { color: var(--accent-a); font-size: 20px; }""")
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
