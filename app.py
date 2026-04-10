import base64
import requests
import hashlib
from flask import Flask, request, render_template_string, Response

app = Flask(__name__)
short_urls = {}

HTML = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>订阅聚合 · SubHub</title>

<style>
*{margin:0;padding:0;box-sizing:border-box;}

body{
    background: linear-gradient(180deg,#f5f5f7,#ffffff);
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto;
    padding:20px;
    color:#1d1d1f;
    min-height:100vh;
}

.container{
    width:100%;
    max-width:1200px;
    margin:0 auto;
}

.card{
    background:rgba(255,255,255,0.8);
    backdrop-filter:blur(20px);
    border-radius:28px;
    padding:32px;
    margin-bottom:20px;
    border:1px solid rgba(0,0,0,0.04);
    box-shadow:0 8px 30px rgba(0,0,0,0.04);
}

.header{
    text-align:center;
    margin-bottom:28px;
}
.header h1{
    font-size:42px;
    font-weight:600;
    background:linear-gradient(135deg,#007aff,#5856d6,#af52de);
    -webkit-background-clip:text;
    background-clip:text;
    color:transparent;
    letter-spacing:-0.5px;
    display:inline-flex;
    align-items:center;
    gap:10px;
    flex-wrap:wrap;
    justify-content:center;
}

@media (min-width: 1024px) {
    body{padding:40px 24px;}
    .card{padding:40px;}
    .header h1{font-size:52px;}
}

@media (min-width: 768px) and (max-width: 1023px) {
    body{padding:30px 24px;}
    .card{padding:32px;}
    .header h1{font-size:44px;}
}

@media (max-width: 767px) {
    body{padding:12px;}
    .card{padding:20px;border-radius:24px;}
    .header h1{font-size:28px;}
    .help-text{font-size:12px;padding:10px 14px;line-height:1.5;}
    .help-text code{font-size:10px;}
    input,textarea{padding:12px 14px;font-size:14px;}
    .btn-primary{padding:14px;font-size:15px;}
    .btn-copy,.btn-test{padding:6px 14px;font-size:12px;}
    .result-title{font-size:14px;}
    .url-box{font-size:11px;padding:12px;}
    .badge{font-size:11px;padding:4px 12px;}
    .node-item{font-size:10px;padding:6px 0;}
}

.help-text{
    background:linear-gradient(135deg,#f8f8fa,#ffffff);
    border-radius:16px;
    padding:12px 20px;
    margin-bottom:28px;
    font-size:13px;
    color:#6e6e73;
    text-align:center;
    border:1px solid rgba(0,122,255,0.1);
}

.help-text code{
    background:#e8e8ed;
    padding:2px 8px;
    border-radius:8px;
    font-size:12px;
    font-family:monospace;
    color:#007aff;
}

.form-group{margin-bottom:20px;}
label{font-size:14px;font-weight:500;display:block;margin-bottom:8px;color:#1d1d1f;}
input,textarea{
    width:100%;
    padding:14px 16px;
    border-radius:14px;
    border:1px solid #d2d2d6;
    font-size:15px;
    transition:0.2s;
    background:#fff;
}
input:focus,textarea:focus{
    border-color:#007aff;
    box-shadow:0 0 0 4px rgba(0,122,255,0.1);
    outline:none;
}
textarea{min-height:120px;resize:vertical;}

.double{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:20px;
    margin-bottom:20px;
}
@media (max-width: 767px){
    .double{grid-template-columns:1fr;gap:12px;}
}

.btn-primary{
    background:linear-gradient(135deg,#007aff,#5856d6);
    color:#fff;
    border:none;
    padding:16px;
    border-radius:16px;
    width:100%;
    font-weight:600;
    font-size:16px;
    cursor:pointer;
    transition:0.2s;
}
.btn-primary:hover{
    background:linear-gradient(135deg,#005fc5,#4640b0);
    transform:scale(0.98);
}

.btn-group{
    display:flex;
    gap:12px;
    flex-wrap:wrap;
    margin-top:12px;
}
.btn-copy,.btn-test{
    padding:8px 18px;
    border:none;
    border-radius:10px;
    background:#e8e8ed;
    cursor:pointer;
    font-size:13px;
    transition:0.2s;
}
.btn-copy:hover,.btn-test:hover{background:#d2d2d6;}

.url-box{
    background:#f5f5f7;
    padding:14px;
    border-radius:14px;
    font-size:12px;
    word-break:break-all;
    font-family:monospace;
    margin:12px 0;
}

.result-section{margin-top:24px;}
.result-title{font-weight:600;margin-bottom:10px;font-size:15px;}

.badge{
    display:inline-block;
    background:linear-gradient(135deg,#007aff,#5856d6);
    color:white;
    padding:4px 14px;
    border-radius:20px;
    font-size:12px;
    margin-bottom:16px;
}

.node-list{
    background:#f5f5f7;
    border-radius:14px;
    padding:12px;
    max-height:260px;
    overflow-y:auto;
    margin-top:16px;
}
.node-item{
    padding:6px 0;
    border-bottom:1px solid #e8e8ed;
    font-family:monospace;
    font-size:11px;
}
.node-item:last-child{border-bottom:none;}

#resultArea{animation:fadeIn 0.3s ease;}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1}}

.toast{
    position:fixed;
    bottom:30px;
    left:50%;
    transform:translateX(-50%);
    background:#1d1d1f;
    color:white;
    padding:10px 22px;
    border-radius:30px;
    font-size:13px;
    z-index:1000;
    white-space:nowrap;
}
@media (max-width: 640px){
    .toast{font-size:12px;padding:8px 16px;white-space:normal;text-align:center;max-width:80%;}
}
</style>
</head>

<body>

<div class="container">

<div class="card">
<div class="header">
<h1>🌐 订阅聚合 · SubHub</h1>
</div>

<div class="help-text">
📖 多个订阅用 <code>|</code> 分隔 · 节点每行一个 · 关键词用 <code>,</code> 分隔<br>
支持 VMess / Trojan / Shadowsocks / VLESS
</div>

<form id="form">
<div class="form-group">
<input name="urls" placeholder="订阅链接 | 示例: https://sub1.com | https://sub2.com">
</div>

<div class="form-group">
<textarea name="raw" placeholder="节点链接（每行一个）&#10;vmess://xxx&#10;trojan://xxx&#10;ss://xxx"></textarea>
</div>

<div class="double">
<div class="form-group">
<input name="include" placeholder="包含关键词 | 示例: 香港,新加坡,日本">
</div>
<div class="form-group">
<input name="exclude" placeholder="排除关键词 | 示例: 过期,失效,流量">
</div>
</div>

<button class="btn-primary" id="submitBtn">✨ 生成订阅</button>
</form>

</div>

<div id="resultArea" style="display:none;">
<div class="card">
<div class="badge" id="nodeCount">✓ 生成成功</div>

<div class="result-section">
<div class="result-title">v2rayN / Shadowrocket</div>
<div id="v2rayUrl" class="url-box"></div>
<div class="btn-group">
<button class="btn-copy" onclick="copyText('v2rayUrl')">📋 复制</button>
<button class="btn-test" onclick="testUrl('v2rayUrl')">🔗 测试</button>
</div>
</div>

<div class="result-section">
<div class="result-title">Clash / Clash Meta</div>
<div id="clashUrl" class="url-box"></div>
<div class="btn-group">
<button class="btn-copy" onclick="copyText('clashUrl')">📋 复制</button>
<button class="btn-test" onclick="testUrl('clashUrl')">🔗 测试</button>
</div>
</div>

<div id="nodeListArea"></div>
</div>
</div>

</div>

<script>
let toastEl = null;
function showToast(msg, isErr){
    if(!toastEl){
        toastEl = document.createElement('div');
        toastEl.className = 'toast';
        document.body.appendChild(toastEl);
    }
    toastEl.textContent = msg;
    toastEl.style.background = isErr ? '#c62828' : '#1d1d1f';
    toastEl.style.display = 'block';
    setTimeout(()=>{toastEl.style.display='none';},2000);
}

async function copyText(id){
    let txt = document.getElementById(id).innerText;
    if(!txt){showToast('无内容',1);return;}
    try{
        await navigator.clipboard.writeText(txt);
        showToast('已复制');
    }catch(e){
        let ta = document.createElement('textarea');
        ta.value = txt;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showToast('已复制');
    }
}

function testUrl(id){
    let url = document.getElementById(id).innerText;
    if(url) window.open(url,'_blank');
}

function showNodeList(nodes, total){
    let container = document.getElementById('nodeListArea');
    if(!nodes || nodes.length===0){container.innerHTML='';return;}
    let html = '<div class="result-section"><div class="result-title">📋 节点列表（前30个）</div><div class="node-list">';
    nodes.slice(0,30).forEach((n,i)=>{
        let s = n.length>80 ? n.substring(0,80)+'...' : n;
        html += `<div class="node-item">${i+1}. ${escapeHtml(s)}</div>`;
    });
    if(total>30) html += `<div class="node-item" style="color:#007aff;">... 还有 ${total-30} 个节点</div>`;
    html += '</div></div>';
    container.innerHTML = html;
}

function escapeHtml(t){
    let div = document.createElement('div');
    div.textContent = t;
    return div.innerHTML;
}

document.getElementById('form').onsubmit = async (e)=>{
    e.preventDefault();
    let btn = document.getElementById('submitBtn');
    let orig = btn.textContent;
    btn.textContent = '⏳ 生成中...';
    btn.disabled = true;

    let fd = new FormData(e.target);
    try{
        let res = await fetch('/api/generate',{method:'POST',body:fd});
        let data = await res.json();
        if(data.error){
            showToast(data.error,1);
            document.getElementById('resultArea').style.display='none';
            return;
        }
        document.getElementById('v2rayUrl').innerText = data.v2ray_url;
        document.getElementById('clashUrl').innerText = data.clash_url;
        document.getElementById('nodeCount').innerHTML = `✓ 生成成功 · ${data.node_count} 个节点`;
        if(data.nodes) showNodeList(data.nodes, data.node_count);
        document.getElementById('resultArea').style.display = 'block';
        showToast(`✓ 生成 ${data.node_count} 个节点`);
        document.getElementById('resultArea').scrollIntoView({behavior:'smooth'});
    }catch(e){
        showToast('请求失败，请检查网络',1);
        document.getElementById('resultArea').style.display='none';
    }finally{
        btn.textContent = orig;
        btn.disabled = false;
    }
};
</script>

</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/generate', methods=['POST'])
def api_generate():
    urls = request.form.get('urls', '')
    raw = request.form.get('raw', '')
    include = request.form.get('include', '')
    exclude = request.form.get('exclude', '')
    
    if not urls and not raw:
        return {'error': '请至少填写订阅链接或节点'}
    
    all_nodes = []
    
    if raw:
        try:
            decoded = base64.b64decode(raw).decode('utf-8')
            for line in decoded.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    all_nodes.append(line)
        except:
            for line in raw.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    all_nodes.append(line)
    
    if urls:
        for url in urls.split('|'):
            url = url.strip()
            if url:
                try:
                    resp = requests.get(url, timeout=10)
                    content = resp.text.strip()
                    try:
                        decoded = base64.b64decode(content).decode('utf-8')
                        content = decoded
                    except:
                        pass
                    for line in content.splitlines():
                        line = line.strip()
                        if line and not line.startswith('#'):
                            all_nodes.append(line)
                except Exception as e:
                    print(f"获取失败: {url} - {e}")
    
    unique_nodes = list(dict.fromkeys(all_nodes))
    
    if include:
        keywords = [k.strip().lower() for k in include.split(',')]
        unique_nodes = [n for n in unique_nodes if any(k in n.lower() for k in keywords)]
    if exclude:
        keywords = [k.strip().lower() for k in exclude.split(',')]
        unique_nodes = [n for n in unique_nodes if not any(k in n.lower() for k in keywords)]
    
    if not unique_nodes:
        return {'error': '没有找到任何有效节点'}
    
    content = '\n'.join(unique_nodes)
    b64_data = base64.b64encode(content.encode()).decode()
    short_id = hashlib.md5(b64_data.encode()).hexdigest()[:8]
    short_urls[short_id] = b64_data
    
    host = request.host_url
    v2ray_url = f"{host}s/{short_id}"
    clash_url = f"{host}c/{short_id}"
    
    return {
        'v2ray_url': v2ray_url,
        'clash_url': clash_url,
        'node_count': len(unique_nodes),
        'nodes': unique_nodes[:50]
    }

@app.route('/s/<sid>')
def get_v2ray(sid):
    if sid not in short_urls:
        return "链接无效或已过期", 404
    data = base64.b64decode(short_urls[sid]).decode()
    return Response(data, mimetype='text/plain; charset=utf-8')

@app.route('/c/<sid>')
def get_clash(sid):
    if sid not in short_urls:
        return "链接无效或已过期", 404
    data = base64.b64decode(short_urls[sid]).decode()
    return Response(data, mimetype='text/yaml; charset=utf-8')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=36963)