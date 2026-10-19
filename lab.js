// Y 形摆交互实验台 —— 真解双角度运动方程 + three.js 实时三维
// 物理约定：x 沿横梁（面内），y 垂直横梁水平（面外），depth 向下为正。
// 世界坐标：(x, -depth, y)，y 轴向上。
import * as THREE from './vendor/three.module.min.js';

const G = 9.81;
const BOB_M = 0.040;          // 摆球质量 / kg
const DEG = Math.PI / 180;

// ------------------------------------------------------------------ 物理
const P = { d: 0.39950, L: 0.320, l: 0.200, gam: 0.03,
            th0: 9, ph0: 9 };
const S = { th: 0, ph: 0, thd: 0, phd: 0, t: 0, running: true };

const hOf = (L, d) => Math.sqrt(Math.max(L * L - (d / 2) ** 2, 1e-9));
const betaOf = (h, l) => Math.sqrt((h + l) / l);
const periods = (h, l) => [2 * Math.PI * Math.sqrt(l / G),
                           2 * Math.PI * Math.sqrt((h + l) / G)];
const thetaCrit = (h, d) => Math.atan((d / 2) / h);

function tensions(th, h, l, d) {
  const a = d / 2, L = Math.hypot(a, h);
  const T3 = BOB_M * G * Math.cos(th);
  const Sm = T3 * Math.cos(th) * L / h;
  const Dv = -T3 * Math.sin(th) * L / a;
  return [(Sm + Dv) / 2, (Sm - Dv) / 2];
}

function rhs(th, ph, thd, phd, h, l, gam) {
  const R = h + l * Math.cos(th);
  const thdd = (-R * Math.sin(th) * phd * phd
                - G * Math.sin(th) * Math.cos(ph)) / l
                - 2 * gam * thd;
  const phdd = (2 * l * Math.sin(th) * thd * phd - G * Math.sin(ph)) / R
                - 2 * gam * phd;
  return [thd, phd, thdd, phdd];
}

function step(dt) {
  const h = hOf(P.L, P.d), l = P.l, gam = P.gam;
  const y = [S.th, S.ph, S.thd, S.phd];
  const k1 = rhs(y[0], y[1], y[2], y[3], h, l, gam);
  const y2 = y.map((v, i) => v + dt / 2 * k1[i]);
  const k2 = rhs(y2[0], y2[1], y2[2], y2[3], h, l, gam);
  const y3 = y.map((v, i) => v + dt / 2 * k2[i]);
  const k3 = rhs(y3[0], y3[1], y3[2], y3[3], h, l, gam);
  const y4 = y.map((v, i) => v + dt * k3[i]);
  const k4 = rhs(y4[0], y4[1], y4[2], y4[3], h, l, gam);
  for (let i = 0; i < 4; i++) {
    y[i] += dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]);
  }
  S.th = y[0]; S.ph = y[1]; S.thd = y[2]; S.phd = y[3];
  S.t += dt;
}

function release() {
  S.th = P.th0 * DEG; S.ph = P.ph0 * DEG;
  S.thd = 0; S.phd = 0; S.t = 0;
  trailLen = 0;
}

function poseOf() {
  const h = hOf(P.L, P.d), l = P.l;
  const R = h + l * Math.cos(S.th);
  const kx = 0, kd = h * Math.cos(S.ph), ky = h * Math.sin(S.ph);
  const bx = l * Math.sin(S.th);
  const bd = R * Math.cos(S.ph);
  const by = R * Math.sin(S.ph);
  // 世界坐标（y 向上）
  const K = new THREE.Vector3(0, -kd, ky);
  const B = new THREE.Vector3(bx, -bd, by);
  return { K, B, h, l, R };
}

// ------------------------------------------------------------------ 场景
const canvas = document.getElementById('c3d');
const stage = document.getElementById('stage');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setClearColor(0x000000, 1);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(38, 1, 0.02, 20);

const hemi = new THREE.HemisphereLight(0xdfe8f5, 0x0a0f16, 1.35);
scene.add(hemi);
const dl = new THREE.DirectionalLight(0xffffff, 1.3);
dl.position.set(1.2, 2.0, 1.4);
scene.add(dl);
const dl2 = new THREE.DirectionalLight(0x88aaff, 0.5);
dl2.position.set(-1.5, 0.6, -1.2);
scene.add(dl2);

const C = {
  frame: 0x8b95a3, frameD: 0x5a6472, brass: 0xc8a24a, screw: 0x9aa6b4,
  str: 0xe6edf7, slack: 0xff5a5a, knot: 0xf2c14e, bob: 0xf7f9fc,
  trace: 0x35c7d8,
};

const mat = (color, opts = {}) => new THREE.MeshStandardMaterial(
  Object.assign({ color, roughness: 0.45, metalness: 0.35 }, opts));

function rodMesh(p1, p2, radius, color, seg = 12) {
  const dir = new THREE.Vector3().subVectors(p2, p1);
  const len = dir.length() || 1e-6;
  const geo = new THREE.CylinderGeometry(radius, radius, len, seg, 1);
  const m = new THREE.Mesh(geo, mat(color));
  m.position.copy(p1).addScaledVector(dir, 0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0),
                                  dir.clone().normalize());
  return m;
}

// ---- 静态门架
const gantry = new THREE.Group();
scene.add(gantry);
const POST = 0.30, FLOOR = 1.02, TOPHALF = 0.33, BASEHY = 0.215;
const v = (x, y, z) => new THREE.Vector3(x, y, z);
{
  for (const sx of [-1, 1]) {
    gantry.add(rodMesh(v(sx * POST, 0, 0), v(sx * POST, -FLOOR, 0), 0.006,
                       C.frame));
  }
  for (const zz of [-1, 1]) {
    gantry.add(rodMesh(v(-TOPHALF, 0, zz * 0.034), v(TOPHALF, 0, zz * 0.034),
                       0.004, C.frameD, 8));
  }
  gantry.add(rodMesh(v(-TOPHALF, 0, 0), v(TOPHALF, 0, 0), 0.0055, 0x66707c));
  // 底部方框
  for (const zz of [-BASEHY, BASEHY]) {
    gantry.add(rodMesh(v(-POST, -FLOOR, zz), v(POST, -FLOOR, zz), 0.006,
                       C.frame, 8));
  }
  for (const xx of [-POST, POST]) {
    gantry.add(rodMesh(v(xx, -FLOOR, -BASEHY), v(xx, -FLOOR, BASEHY), 0.006,
                       C.frame, 8));
  }
  // 螺纹（一条细螺旋线，表现丝杆可转）
  const pts = [];
  const N = 2600;
  for (let i = 0; i <= N; i++) {
    const t = i / N;
    const xx = -TOPHALF + 0.012 + t * (2 * TOPHALF - 0.024);
    const a = (xx / 0.008) * Math.PI * 2;
    pts.push(new THREE.Vector3(xx, 0.0055 * Math.cos(a),
                               0.0055 * Math.sin(a)));
  }
  const tg = new THREE.BufferGeometry().setFromPoints(pts);
  const thread = new THREE.Line(tg, new THREE.LineBasicMaterial(
    { color: C.screw, transparent: true, opacity: 0.55 }));
  gantry.add(thread);
}

// ---- 两个法兰 + 三根绳 + 结点 + 摆球
const flanges = [];
for (let i = 0; i < 2; i++) {
  const g = new THREE.Group();
  const box = new THREE.Mesh(new THREE.BoxGeometry(0.10, 0.050, 0.076),
                             mat(C.brass, { roughness: 0.35, metalness: 0.7 }));
  g.add(box);
  const ear = rodMesh(v(0, -0.025, 0), v(0, -0.055, 0), 0.007, C.brass, 8);
  g.add(ear);
  gantry.add(g);
  flanges.push(g);
}

const sL = rodMesh(v(0, 0, 0), v(0, -0.01, 0), 0.0016, C.str, 6);
const sR = rodMesh(v(0, 0, 0), v(0, -0.01, 0), 0.0016, C.str, 6);
const sB = rodMesh(v(0, 0, 0), v(0, -0.01, 0), 0.0016, C.str, 6);
scene.add(sL, sR, sB);

const knot = new THREE.Mesh(new THREE.SphereGeometry(0.009, 16, 12),
                            mat(C.knot, { metalness: 0.2 }));
scene.add(knot);

const bob = new THREE.Mesh(new THREE.SphereGeometry(0.013, 24, 18),
                           mat(C.bob, { roughness: 0.25, metalness: 0.1 }));
scene.add(bob);
const bobHalo = new THREE.Mesh(new THREE.SphereGeometry(0.022, 16, 12),
  new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true,
                                opacity: 0.08 }));
scene.add(bobHalo);

// ---- 轨迹
const MAXPTS = 24000;
const trailPos = new Float32Array(MAXPTS * 3);
const trailGeo = new THREE.BufferGeometry();
trailGeo.setAttribute('position', new THREE.BufferAttribute(trailPos, 3));
trailGeo.setDrawRange(0, 0);
const trail = new THREE.Line(trailGeo, new THREE.LineBasicMaterial(
  { color: C.trace, transparent: true, opacity: 0.95 }));
trail.frustumCulled = false;
scene.add(trail);
let trailLen = 0;

function pushTrail(p) {
  if (trailLen >= MAXPTS) return;
  const i = trailLen * 3;
  trailPos[i] = p.x; trailPos[i + 1] = p.y; trailPos[i + 2] = p.z;
  trailLen++;
  trailGeo.setDrawRange(0, trailLen);
  trailGeo.attributes.position.needsUpdate = true;
}

// ------------------------------------------------------------------ 相机
const TARGET = new THREE.Vector3(0, -0.50, 0);
const orb = { r: 2.05, phi: 70 * DEG, theta: -52 * DEG };
const VIEWS = {
  iso: { r: 2.05, phi: 70 * DEG, theta: -52 * DEG },
  front: { r: 2.10, phi: 90 * DEG, theta: -90 * DEG },
  top: { r: 1.55, phi: 8 * DEG, theta: -90 * DEG },
};

function applyCam() {
  const { r, phi, theta } = orb;
  camera.position.set(
    TARGET.x + r * Math.sin(phi) * Math.cos(theta),
    TARGET.y + r * Math.cos(phi),
    TARGET.z + r * Math.sin(phi) * Math.sin(theta));
  camera.lookAt(TARGET);
}

(function bindOrbit() {
  let down = false, lx = 0, ly = 0, pid = null, pinch = 0;
  const pts = new Map();
  stage.addEventListener('pointerdown', (e) => {
    pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pts.size === 1) { down = true; lx = e.clientX; ly = e.clientY; }
    stage.setPointerCapture(e.pointerId);
  });
  stage.addEventListener('pointermove', (e) => {
    if (!pts.has(e.pointerId)) return;
    pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pts.size === 2) {
      const [a, b] = [...pts.values()];
      const d = Math.hypot(a.x - b.x, a.y - b.y);
      if (pinch) {
        orb.r = Math.min(5.0, Math.max(0.35, orb.r * pinch / d));
        applyCam();
      }
      pinch = d;
      return;
    }
    if (!down) return;
    const dx = e.clientX - lx, dy = e.clientY - ly;
    lx = e.clientX; ly = e.clientY;
    orb.theta -= dx * 0.008;
    orb.phi = Math.min(168 * DEG, Math.max(6 * DEG, orb.phi - dy * 0.006));
    applyCam();
  });
  const up = (e) => {
    pts.delete(e.pointerId);
    if (pts.size < 2) pinch = 0;
    if (pts.size === 0) down = false;
  };
  stage.addEventListener('pointerup', up);
  stage.addEventListener('pointercancel', up);
  stage.addEventListener('wheel', (e) => {
    e.preventDefault();
    orb.r = Math.min(5.0, Math.max(0.35, orb.r * (1 + Math.sign(e.deltaY) * 0.08)));
    applyCam();
  }, { passive: false });
})();

document.querySelectorAll('[data-view]').forEach((b) => {
  b.addEventListener('click', () => {
    Object.assign(orb, VIEWS[b.dataset.view]);
    applyCam();
  });
});

// ------------------------------------------------------------------ 尺寸
function resize() {
  const w = stage.clientWidth, hgt = stage.clientHeight;
  renderer.setSize(w, hgt, false);
  camera.aspect = w / hgt;
  camera.updateProjectionMatrix();
}
window.addEventListener('resize', resize);

// ------------------------------------------------------------------ 更新摆
let curPose = null;
function updateRig() {
  const { K, B } = poseOf();
  curPose = { K, B };
  const d = P.d;
  flanges[0].position.set(-d / 2, 0, 0);
  flanges[1].position.set(d / 2, 0, 0);

  const A1 = v(-d / 2, -0.055, 0);
  const A2 = v(d / 2, -0.055, 0);

  function placeString(mesh, p1, p2, color) {
    const dir = new THREE.Vector3().subVectors(p2, p1);
    const len = dir.length() || 1e-6;
    mesh.position.copy(p1).addScaledVector(dir, 0.5);
    mesh.scale.set(1, len, 1);
    mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0),
                                       dir.clone().normalize());
    mesh.material.color.setHex(color);
  }
  const [T1, T2] = tensions(S.th, hOf(P.L, P.d), P.l, P.d);
  placeString(sL, A1, K, T1 > 0 ? C.str : C.slack);
  placeString(sR, A2, K, T2 > 0 ? C.str : C.slack);
  placeString(sB, K, B, C.str);
  knot.position.copy(K);
  bob.position.copy(B);
  bobHalo.position.copy(B);
  return { T1, T2 };
}

// 单位圆柱沿 y，高度 1，便于用 scale.y 拉伸
for (const m of [sL, sR, sB]) {
  m.geometry.dispose();
  m.geometry = new THREE.CylinderGeometry(0.0016, 0.0016, 1, 6, 1);
}

// ------------------------------------------------------------------ 读数
const el = (id) => document.getElementById(id);
function ratioText(b) {
  let best = null;
  for (let q = 1; q <= 12; q++) {
    const p = Math.round(b * q);
    if (p < 1) continue;
    const err = Math.abs(b - p / q) / b;
    if (!best || err < best[2]) best = [p, q, err];
  }
  if (best && best[2] <= 0.004) return [`${best[0]} : ${best[1]}`, true];
  return [b.toFixed(4), false];
}

function refreshReadout() {
  const h = hOf(P.L, P.d);
  const b = betaOf(h, P.l);
  const [Tx, Ty] = periods(h, P.l);
  const crit = thetaCrit(h, P.d) / DEG;
  // 准静态张力：T3 = m g cos(theta)。真实摆动还要加 l*theta_dot^2，会更大。
  const [T1, T2] = tensions(S.th, h, P.l, P.d);
  const [btxt, exact] = ratioText(b);
  const m = /^(\d+)\s*:\s*(\d+)$/.exec(btxt);
  const tc = m ? Number(m[1]) * Tx : null;   // 3:2 -> 3*T_x

  el('o-h').textContent = (h * 100).toFixed(2) + ' cm';
  el('o-b').textContent = btxt;
  el('o-b').style.color = exact ? 'var(--accent-b)' : 'var(--accent-a)';
  el('o-tx').textContent = Tx.toFixed(4) + ' s';
  el('o-ty').textContent = Ty.toFixed(4) + ' s';
  el('o-tc').textContent = tc ? tc.toFixed(4) + ' s' : '无公共周期';
  el('o-crit').textContent = crit.toFixed(1) + '°';
  el('o-t1').textContent = (T1 / (BOB_M * G)).toFixed(2) + ' mg';
  el('o-t2').textContent = (T2 / (BOB_M * G)).toFixed(2) + ' mg';
  el('o-t1').className = T1 > 0 ? '' : 'warnv';
  el('o-t2').className = T2 > 0 ? '' : 'warnv';

  const over = Math.abs(S.th) / DEG > crit || Math.abs(S.ph) / DEG > crit;
  document.getElementById('warn').className = over ? 'lab-badge on' : 'lab-badge';
  return { b, h, Tx, Ty };
}

// ------------------------------------------------------------------ UI
const bind = (id, key, fmt, scale) => {
  const s = el(id), lab = el('v-' + key);
  const upd = () => {
    P[key] = parseFloat(s.value) * (scale || 1);
    lab.textContent = fmt(parseFloat(s.value));
  };
  s.addEventListener('input', () => {
    upd();
    if (key === 'th0' || key === 'ph0') release();
    refreshReadout();
  });
  upd();
  return s;
};

bind('s-d', 'd', (x) => x.toFixed(2) + ' cm', 0.01);
bind('s-L', 'L', (x) => x.toFixed(2) + ' cm', 0.01);
bind('s-l', 'l', (x) => x.toFixed(2) + ' cm', 0.01);
bind('s-th', 'th0', (x) => x.toFixed(1) + '°', 1);
bind('s-ph', 'ph0', (x) => x.toFixed(1) + '°', 1);
bind('s-g', 'gam', (x) => x.toFixed(2) + ' s⁻¹', 1);

document.getElementById('btn-go').addEventListener('click', () => {
  release(); S.running = true;
  document.getElementById('btn-pause').textContent = '暂停';
});
document.getElementById('btn-pause').addEventListener('click', (e) => {
  S.running = !S.running;
  e.target.textContent = S.running ? '暂停' : '继续';
});
document.getElementById('btn-clear').addEventListener('click', () => {
  trailLen = 0; trailGeo.setDrawRange(0, 0);
});

function setSlider(id, value) {
  const s = el(id);
  s.value = String(value);
  s.dispatchEvent(new Event('input'));
}

document.querySelectorAll('[data-preset]').forEach((b) => {
  b.addEventListener('click', () => {
    const k = b.dataset.preset;
    // 全部按 L = 32 cm、l = 20 cm 的实物来；比例靠改 d 或 l 得到
    if (k === '32') {                       // 当前设计点
      setSlider('s-d', 39.95); setSlider('s-L', 32); setSlider('s-l', 20);
      setSlider('s-th', 9); setSlider('s-ph', 9);
    } else if (k === '21') {                // 下绳缩短到 9.42 cm
      setSlider('s-d', 30); setSlider('s-L', 32); setSlider('s-l', 9.42);
      setSlider('s-th', 8); setSlider('s-ph', 8);
    } else if (k === '54') {                // 拉开悬点间距
      setSlider('s-d', 59.92); setSlider('s-L', 32); setSlider('s-l', 20);
      setSlider('s-th', 9); setSlider('s-ph', 9);
    } else if (k === 'crit') {              // 越过 38.6 度松绳临界
      setSlider('s-d', 39.95); setSlider('s-L', 32); setSlider('s-l', 20);
      setSlider('s-th', 42); setSlider('s-ph', 2);
    } else if (k === 'irr') {               // beta = sqrt(2)
      setSlider('s-d', 49.96); setSlider('s-L', 32); setSlider('s-l', 20);
      setSlider('s-th', 9); setSlider('s-ph', 9);
    }
    release(); S.running = true;
    document.getElementById('btn-pause').textContent = '暂停';
    refreshReadout();
  });
});

// ------------------------------------------------------------------ 主循环
resize();
applyCam();
release();
refreshReadout();

let last = performance.now();
let acc = 0;
const FIXED = 1 / 480;
let frameCount = 0;

function loop(now) {
  requestAnimationFrame(loop);
  const dtWall = Math.min((now - last) / 1000, 0.05);
  last = now;

  if (S.running) {
    acc += dtWall;
    let guard = 0;
    while (acc >= FIXED && guard < 2000) {
      step(FIXED);
      acc -= FIXED;
      guard++;
    }
  }
  updateRig();
  frameCount++;
  if (S.running && frameCount % 2 === 0) pushTrail(curPose.B);
  if (frameCount % 6 === 0) refreshReadout();
  renderer.render(scene, camera);
}
requestAnimationFrame(loop);
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
  const advSec = parseFloat(q.get('adv') || '0');
  if (advSec > 0) {
    // 直接推进仿真，用来核对积分器（无头浏览器不给 rAF 帧）
    const n = Math.round(advSec / FIXED);
    for (let i = 0; i < n; i++) step(FIXED);
    pushTrail(poseOf().B);
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
})();
