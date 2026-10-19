import io
# ---------------- lab.html：滑块精度 + 初始值
p="lab.html"; s=io.open(p,encoding="utf-8").read()
s=s.replace('<input type="range" id="s-d" min="10" max="40" step="0.1" value="30">',
            '<input type="range" id="s-d" min="10" max="40" step="0.01" value="30">')
s=s.replace('<input type="range" id="s-L" min="26" max="46" step="0.1" value="38.1">',
            '<input type="range" id="s-L" min="26" max="46" step="0.01" value="38.08">')
s=s.replace('<input type="range" id="s-l" min="6" max="50" step="0.1" value="45">',
            '<input type="range" id="s-l" min="6" max="50" step="0.01" value="45">')
s=s.replace('<span id="v-d">30.0 cm</span>','<span id="v-d">30.00 cm</span>')
s=s.replace('<span id="v-L">38.1 cm</span>','<span id="v-L">38.08 cm</span>')
s=s.replace('<span id="v-l">45.0 cm</span>','<span id="v-l">45.00 cm</span>')
io.open(p,"w",encoding="utf-8").write(s)

# ---------------- lab.js
p="lab.js"; s=io.open(p,encoding="utf-8").read()
s=s.replace("const TARGET = new THREE.Vector3(0, -0.45, 0);",
            "const TARGET = new THREE.Vector3(0, -0.50, 0);")
s=s.replace("const orb = { r: 1.35, phi: 68 * DEG, theta: -52 * DEG };",
            "const orb = { r: 2.05, phi: 70 * DEG, theta: -52 * DEG };")
s=s.replace("""const VIEWS = {
  iso: { r: 1.35, phi: 68 * DEG, theta: -52 * DEG },
  front: { r: 1.45, phi: 90 * DEG, theta: -90 * DEG },
  top: { r: 1.15, phi: 8 * DEG, theta: -90 * DEG },
};""","""const VIEWS = {
  iso: { r: 2.05, phi: 70 * DEG, theta: -52 * DEG },
  front: { r: 2.10, phi: 90 * DEG, theta: -90 * DEG },
  top: { r: 1.55, phi: 8 * DEG, theta: -90 * DEG },
};""")
s=s.replace("orb.r = Math.min(4.0, Math.max(0.5, orb.r * pinch / d));",
            "orb.r = Math.min(5.0, Math.max(0.35, orb.r * pinch / d));")
s=s.replace("orb.r = Math.min(4.0, Math.max(0.5, orb.r * (1 + Math.sign(e.deltaY) * 0.08)));",
            "orb.r = Math.min(5.0, Math.max(0.35, orb.r * (1 + Math.sign(e.deltaY) * 0.08)));")
# 数字格式：d/L/l 用两位小数
s=s.replace("bind('s-d', 'd', (x) => x.toFixed(1) + ' cm', 0.01);",
            "bind('s-d', 'd', (x) => x.toFixed(2) + ' cm', 0.01);")
s=s.replace("bind('s-L', 'L', (x) => x.toFixed(1) + ' cm', 0.01);",
            "bind('s-L', 'L', (x) => x.toFixed(2) + ' cm', 0.01);")
s=s.replace("bind('s-l', 'l', (x) => x.toFixed(1) + ' cm', 0.01);",
            "bind('s-l', 'l', (x) => x.toFixed(2) + ' cm', 0.01);")
# β 精确时标金色
s=s.replace("  el('o-b').textContent = btxt + (exact ? '' : '');",
            "  el('o-b').textContent = btxt;\n  el('o-b').style.color = exact ? 'var(--accent-b)' : 'var(--accent-a)';")
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
