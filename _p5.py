import io
p="lab.js"; s=io.open(p,encoding="utf-8").read()
s=s.replace('''  setTimeout(() => {
    const h = hOf(P.L, P.d);''','''  const advSec = parseFloat(q.get('adv') || '0');
  if (advSec > 0) {
    // 直接推进仿真，用来核对积分器（无头浏览器不给 rAF 帧）
    const n = Math.round(advSec / FIXED);
    for (let i = 0; i < n; i++) step(FIXED);
    pushTrail(poseOf().B);
  }
  setTimeout(() => {
    const h = hOf(P.L, P.d);''')
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
