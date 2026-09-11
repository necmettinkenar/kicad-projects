#!/usr/bin/env python3
"""Build self-contained interactive 3D PCB viewer HTML (three.js + GLB embedded as base64)."""
import base64, os

DOC = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller\documentation'
TMP = os.environ['TEMP']

glb_b64 = base64.b64encode(open(os.path.join(DOC, 'pcb_3d.glb'), 'rb').read()).decode()
three = open(os.path.join(TMP, 'three.min.js'), encoding='utf-8').read()
gltf = open(os.path.join(TMP, 'GLTFLoader.js'), encoding='utf-8').read()
orbit = open(os.path.join(TMP, 'OrbitControls.js'), encoding='utf-8').read()

html = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Step Motor Controller — 3B Görüntüleyici</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#1a1e24;color:#dfe3e8;font-family:Georgia,serif;overflow:hidden}
#app{position:fixed;inset:0}
#hud{position:fixed;top:16px;left:16px;background:rgba(16,20,26,.88);border:1px solid #3a414b;
     padding:14px 20px;max-width:420px;user-select:none}
#hud h1{font-size:17px;margin-bottom:4px;color:#e8b168}
#hud p{font-size:12px;color:#9aa3ad;line-height:1.5}
#hud .k{color:#dfe3e8}
#bar{position:fixed;bottom:14px;left:50%;transform:translateX(-50%);background:rgba(16,20,26,.88);
     border:1px solid #3a414b;padding:8px 18px;font-size:12.5px;color:#9aa3ad;display:flex;gap:22px}
#bar b{color:#e8b168;font-weight:600}
#loading{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;
         background:#1a1e24;color:#e8b168;font-size:15px;z-index:10}
button.vw{background:#242b33;border:1px solid #3a414b;color:#dfe3e8;padding:5px 12px;cursor:pointer;
          font-size:12px;margin-right:6px}
button.vw:hover{border-color:#e8b168;color:#e8b168}
</style>
</head>
<body>
<div id="app"></div>
<div id="loading">3B model yükleniyor…</div>
<div id="hud">
  <h1>Step Motor Controller</h1>
  <p><span class="k">34 bileşen</span> · 100×80 mm · 2 katman<br>
  ESP32-DevKitC + LV8729 step sürücü + AM26LS32 enkoder alıcısı + IRM-20-24 güç modülü</p>
  <p style="margin-top:8px">Sürükle: döndür · Tekerlek: yakınlaştır · Sağ tık sürükle: kaydır</p>
  <p style="margin-top:8px">
    <button class="vw" onclick="setView(0,-90)">Üst</button>
    <button class="vw" onclick="setView(0,90)">Alt</button>
    <button class="vw" onclick="setView(35,-35)">Eğik</button>
    <button class="vw" onclick="setView(5,0)">Ön</button>
  </p>
</div>
<div id="bar"><span>Kamera: <b id="mode">Eğik</b></span><span>Model: <b>PCB (bileşen pad'li)</b></span><span>Dosya: <b>pcb_3d.glb</b></span></div>
<script>__THREE__</script>
<script>__GLTF__</script>
<script>__ORBIT__</script>
<script>
const GLB_B64 = "__GLBB64__";
let camera, renderer, scene, controls, board;
const container = document.getElementById('app');
scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1e24);
camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 1, 5000);
renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.outputEncoding = THREE.sRGBEncoding;
container.appendChild(renderer.domElement);
controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
const hemi = new THREE.HemisphereLight(0xffffff, 0x33383f, 0.9);
scene.add(hemi);
const dir1 = new THREE.DirectionalLight(0xffffff, 0.85); dir1.position.set(80, 120, 90); scene.add(dir1);
const dir2 = new THREE.DirectionalLight(0xfff2e0, 0.4); dir2.position.set(-60, -40, -80); scene.add(dir2);

// grid floor
const grid = new THREE.GridHelper(300, 30, 0x2e353d, 0x232a31);
grid.position.y = -3; scene.add(grid);

function setView(polar, azimuth){
  const r = 170;
  const phi = polar * Math.PI/180, theta = azimuth * Math.PI/180;
  camera.position.set(
    r * Math.sin(phi) * Math.sin(theta),
    r * Math.cos(phi),
    r * Math.sin(phi) * Math.cos(theta));
  controls.target.set(0, 0, 0);
  controls.update();
  document.getElementById('mode').textContent =
    (polar===0&&azimuth===-90)?'Üst':(polar===0&&azimuth===90)?'Alt':(polar===5)?'Ön':'Eğik';
}

const loader = new THREE.GLTFLoader();
const bin = atob(GLB_B64);
const bytes = new Uint8Array(bin.length);
for (let i=0;i<bin.length;i++) bytes[i] = bin.charCodeAt(i);
const blob = new Blob([bytes], {type:'model/gltf-binary'});
const url = URL.createObjectURL(blob);
loader.load(url, function(gltf){
  board = gltf.scene;
  const box = new THREE.Box3().setFromObject(board);
  const size = box.getSize(new THREE.Vector3());
  const center = box.getCenter(new THREE.Vector3());
  board.position.sub(center);
  // KiCad Z-up → three.js Y-up
  board.rotation.x = -Math.PI/2;
  scene.add(board);
  document.getElementById('loading').style.display = 'none';
  setView(35, -35);
}, undefined, function(err){
  document.getElementById('loading').textContent = 'Model yüklenemedi: ' + err;
});

window.addEventListener('resize', function(){
  camera.aspect = window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

function animate(){
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();
</script>
</body>
</html>"""

html = html.replace('__THREE__', three).replace('__GLTF__', gltf).replace('__ORBIT__', orbit)
html = html.replace('__GLBB64__', glb_b64)

out = os.path.join(DOC, 'pcb-3d-viewer.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Viewer written: {out} ({os.path.getsize(out)//1024} KB)')
