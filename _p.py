import io
p="lab.html"; s=io.open(p,encoding="utf-8").read()
s=s.replace('''  window.addEventListener('error', function (e) {
    var s = document.getElementById('stage');
    if (s && !window.__lab_ok) {
      s.innerHTML = '<div class="nolab">这个浏览器没能启用 3D 渲染（WebGL）。' +
        '可以先回 <a href="index.html">总目录</a> 看录好的动画。</div>';
    }
  });''','''  window.addEventListener('error', function (e) {
    var s = document.getElementById('stage');
    if (s && !window.__lab_ok) {
      var msg = (e && (e.message || (e.error && e.error.message))) || 'unknown';
      s.innerHTML = '<div class="nolab">3D 没能启动：<br>' +
        String(msg) + '<br><br>可以先回 <a href="index.html">总目录</a> 看录好的动画。</div>';
      s.setAttribute('data-err', String(msg));
    }
  });''')
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
