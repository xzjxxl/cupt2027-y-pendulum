import io
p="lab.js"; s=io.open(p,encoding="utf-8").read()
s=s.replace("requestAnimationFrame(loop);\nwindow.__lab_ok = true;",
'''requestAnimationFrame(loop);
window.__lab_ok = true;

// ---- 自检钩子：?probe=1 时把运行状态写进 title，方便无头浏览器核对
(function probe() {
  const q = new URLSearchParams(location.search);
  if (!q.has('probe')) return;
  const preset = q.get('probe');
  if (preset && preset !== '1') {
    const b = document.querySelector('[data-preset="' + preset + '"]');
    if (b) b.click();
  }
  setTimeout(() => {
    const h = hOf(P.L, P.d);
    const b = betaOf(h, P.l);
    const [Tx, Ty] = periods(h, P.l);
    document.title = 'PROBE ok=' + (window.__lab_ok ? 1 : 0)
      + ' t=' + S.t.toFixed(2)
      + ' th=' + (S.th / DEG).toFixed(2)
      + ' trail=' + trailLen
      + ' d=' + (P.d * 100).toFixed(2)
      + ' h=' + (h * 100).toFixed(2)
      + ' beta=' + b.toFixed(4)
      + ' Tx=' + Tx.toFixed(4) + ' Ty=' + Ty.toFixed(4);
  }, 5000);
})();''')
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
