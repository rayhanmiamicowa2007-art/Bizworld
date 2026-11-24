from flask import Flask, request, redirect, url_for, render_template_string
from urllib.parse import quote
import json, os, base64, time

app = Flask(__name__)
DATA_FILE = "businesses.json"
ADMIN_PIN = "1995"
OWNER_PHONE = "265986765421"

PWA_HEAD = """
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#0f172a">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Bizworld">
<link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/744/744465.png">
<link rel="icon" href="https://cdn-icons-png.flaticon.com/512/744/744465.png">
"""

DEFAULT = [
    {"name": "Lilongwe Fresh Foods", "category": "Food", "city": "Lilongwe", "desc": "Fresh vegetables, fruits & groceries delivered in Area 47.", "price": "From K2,000", "phone": "265880123456", "location": "Area 47, Lilongwe", "featured": True, "images": [], "video": "", "updated": 0},
    {"name": "Glow Beauty Salon", "category": "Beauty", "city": "Lilongwe", "desc": "Braiding, nails, makeup & wigs. Walk-ins welcome.", "price": "From K5,000", "phone": "265991234567", "location": "Old Town, Lilongwe", "featured": True, "images": [], "video": "", "updated": 0},
    {"name": "TechFix Malawi", "category": "Phones", "city": "Lilongwe", "desc": "Phone repair, screens, batteries & accessories in 30 mins.", "price": "From K10,000", "phone": "265882345678", "location": "City Centre, Lilongwe", "featured": False, "images": [], "video": "", "updated": 0},
    {"name": "Urban Styles Boutique", "category": "Fashion", "city": "Blantyre", "desc": "Latest fashion, shoes & bags for men & women.", "price": "From K15,000", "phone": "265993456789", "location": "Chichiri, Blantyre", "featured": False, "images": [], "video": "", "updated": 0},
    {"name": "HomeClean Services", "category": "Services", "city": "Blantyre", "desc": "House cleaning, laundry & fumigation. Book same day.", "price": "From K20,000", "phone": "265884567890", "location": "All Blantyre", "featured": False, "images": [], "video": "", "updated": 0},
    {"name": "Mama's Kitchen", "category": "Food", "city": "Lilongwe", "desc": "Nsima, Chambo, Beef & local dishes. Lunch delivery.", "price": "From K4,500", "phone": "265995678901", "location": "Area 18, Lilongwe", "featured": False, "images": [], "video": "", "updated": 0},
]

def load():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                data = json.load(f)
                for b in data:
                    if "city" not in b: b["city"] = "Lilongwe"
                    if "video" not in b: b["video"] = ""
                    if "updated" not in b: b["updated"] = 0
                    if "images" not in b:
                        old = b.get("image","")
                        b["images"] = [old] if old else []
                return data
        except: return DEFAULT.copy()
    return DEFAULT.copy()
def save(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

BUSINESSES = load()
CATEGORIES = ["All", "Food", "Fashion", "Beauty", "Phones", "Services"]
CITIES = ["All", "Lilongwe", "Blantyre", "Mzuzu", "Zomba", "Mzimba"]
EMOJI = {"Food": "🍲", "Fashion": "👗", "Beauty": "💅", "Phones": "📱", "Services": "🧹"}

STYLE = PWA_HEAD + """
<script>
if ('serviceWorker' in navigator) { navigator.serviceWorker.register('/sw.js'); }
</script>
<style>
* {box-sizing:border-box; font-family:'Segoe UI',Arial,sans-serif;}
body {margin:0; background:#f6f7fb; color:#111;}
header {background:#0f172a; color:white; padding:28px 16px; text-align:center;}
header h1 {margin:0; font-size:32px;} header p {opacity:.85; margin:8px 0 16px;}
header a {background:#22c55e; color:white; padding:11px 18px; border-radius:999px; text-decoration:none; font-weight:700; display:inline-block; margin:4px;}
header a.gold {background:#f59e0b; color:#111;}
.install {background:white !important; color:#0f172a !important; border:2px solid #22c55e;}
.search {max-width:900px; margin:-18px auto 0; background:white; padding:14px; border-radius:14px; box-shadow:0 8px 30px rgba(0,0,0,.1); display:flex; gap:8px; flex-wrap:wrap;}
.search input {flex:1; min-width:160px; padding:12px; border:1px solid #ddd; border-radius:10px;}
.search select, .search button {padding:12px; border-radius:10px; border:1px solid #ddd;}
.search button {background:#0f172a; color:white; border:none; font-weight:700;}
.cats {max-width:900px; margin:16px auto; padding:0 12px; display:flex; gap:8px; flex-wrap:wrap;}
.cats a {background:white; padding:8px 14px; border-radius:999px; text-decoration:none; color:#111; border:1px solid #e5e5e5;}
.cats a.active {background:#0f172a; color:white;}
.cats a.city-active {background:#16a34a; color:white;}
.grid {max-width:900px; margin:0 auto; padding:12px; display:grid; grid-template-columns:1fr 1fr; gap:14px;}
@media(max-width:600px){.grid{grid-template-columns:1fr;}}
.card {background:white; border-radius:16px; overflow:hidden; box-shadow:0 4px 18px rgba(0,0,0,.06); position:relative;}
.card-img {height:220px; background:#e0e7ff; display:flex; align-items:center; justify-content:center; font-size:60px; overflow:hidden;}
.card-img img {width:100%; height:100%; object-fit:cover;}
.thumbs {display:flex; gap:6px; padding:8px 8px 0;}
.thumbs img {width:60px; height:60px; object-fit:cover; border-radius:8px; cursor:pointer; border:2px solid #eee;}
.thumbs img.active {border-color:#22c55e;}
.card-body {padding:16px;}
.badge {display:inline-block; background:#e0f2fe; color:#0369a1; padding:4px 10px; border-radius:999px; font-size:12px; font-weight:700;}
.badge-city {background:#dcfce7; color:#166534;}
.featured {background:#fef3c7; color:#92400e;}
.newstock {background:#dcfce7; color:#166534; border:1px solid #22c55e;}
.card h3 {margin:10px 0 6px;} .card p {color:#555; font-size:14px; line-height:1.5;}
.price {font-weight:800; color:#16a34a;}
.wa {display:block; text-align:center; background:#22c55e; color:white; padding:12px; border-radius:10px; text-decoration:none; font-weight:800; margin-top:12px;}
.vid {display:block; text-align:center; background:#111; color:white; padding:10px; border-radius:10px; text-decoration:none; font-weight:700; margin-top:8px;}
.update {display:block; text-align:center; background:white; color:#0f172a; border:1px solid #ddd; padding:10px; border-radius:10px; text-decoration:none; font-weight:700; margin-top:8px;}
.del {position:absolute; top:8px; right:8px; background:#ef4444; color:white; border-radius:50%; width:28px; height:28px; text-align:center; line-height:28px; text-decoration:none; font-weight:800; z-index:5;}
footer {text-align:center; padding:24px; color:#777; font-size:13px;}
.form {max-width:600px; margin:20px auto; background:white; padding:20px; border-radius:16px;}
.form input, .form select, .form textarea {width:100%; padding:12px; margin:8px 0; border:1px solid #ddd; border-radius:10px;}
.form button {width:100%; padding:14px; background:#0f172a; color:white; border:none; border-radius:10px; font-weight:800;}
.plan {background:white; border-radius:16px; padding:20px; margin:12px 0; border:2px solid #eee;}
.plan.hot {border-color:#f59e0b; background:#fffbeb;}
small {color:#888;}
label {font-weight:700; font-size:13px;}
.install-banner {display:none; max-width:900px; margin:12px auto; background:#0f172a; color:white; padding:14px; border-radius:14px; text-align:center;}
.install-banner button {background:#22c55e; color:white; border:none; padding:10px 18px; border-radius:999px; font-weight:800; margin-left:8px;}
</style>
<script>
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  document.getElementById('installBanner').style.display = 'block';
});
function installApp(){
  if(deferredPrompt){ deferredPrompt.prompt(); deferredPrompt.userChoice.then(()=>{ deferredPrompt=null; document.getElementById('installBanner').style.display='none'; }); }
  else { alert('To install: Tap 3 dots in Chrome > Install app / Add to Home screen. On iPhone: Share > Add to Home Screen'); }
}
function swap(cardId, src, el){
  document.getElementById('main-'+cardId).src = src;
  var thumbs = el.parentElement.querySelectorAll('img');
  thumbs.forEach(t=>t.classList.remove('active'));
  el.classList.add('active');
}
</script>
"""

@app.route('/manifest.json')
def manifest():
    return {
        "name": "Bizworld Malawi",
        "short_name": "Bizworld",
        "description": "Find the best businesses in Malawi. Order on WhatsApp.",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0f172a",
        "theme_color": "#0f172a",
        "icons": [
            {"src": "https://cdn-icons-png.flaticon.com/512/744/744465.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "https://cdn-icons-png.flaticon.com/512/744/744465.png", "sizes": "192x192", "type": "image/png", "purpose": "any"}
        ]
    }

@app.route('/sw.js')
def sw():
    return "self.addEventListener('install', e => { self.skipWaiting(); }); self.addEventListener('fetch', e => { e.respondWith(fetch(e.request).catch(()=>caches.match(e.request))); });", 200, {'Content-Type': 'application/javascript'}

def build_thumbs(idx, images):
    parts = []
    for i, im in enumerate(images):
        cls = "active" if i == 0 else ""
        part = "<img src='" + im + "' class='" + cls + "' onclick=\"swap(" + str(idx) + ", '" + im + "', this)\">"
        parts.append(part)
    return "<div class='thumbs'>" + "".join(parts) + "</div>"

@app.route('/')
def home():
    q = request.args.get('q','').lower().strip()
    cat = request.args.get('cat','All')
    city = request.args.get('city','All')
    admin = request.args.get('admin') == '1'
    filtered = BUSINESSES
    if cat != 'All': filtered = [b for b in filtered if b['category']==cat]
    if city != 'All': filtered = [b for b in filtered if b.get('city','Lilongwe')==city]
    if q: filtered = [b for b in filtered if q in b['name'].lower() or q in b['desc'].lower() or q in b['location'].lower() or q in b['category'].lower() or q in b.get('city','').lower()]
    indexed = [(BUSINESSES.index(b), b) for b in filtered]
    indexed = sorted(indexed, key=lambda x: (not x[1].get('featured', False), not (time.time() - x[1].get('updated',0) < 7*24*3600)))
    cards=""
    for idx, b in indexed:
        wa_text = quote("Hi " + b['name'] + "! I found you on Bizworld. I want to order / enquire.")
        feat = "<span class='badge featured'>⭐ Featured</span> " if b.get('featured') else ""
        is_new = time.time() - b.get('updated',0) < 7*24*3600 and b.get('updated',0) > 0
        new_badge = "<span class='badge newstock'>🆕 NEW STOCK!</span> " if is_new else ""
        images = b.get('images', [])
        if images:
            main_img = "<img id='main-" + str(idx) + "' src='" + images[0] + "'>"
            thumbs_html = ""
            if len(images) > 1:
                thumbs_html = build_thumbs(idx, images)
            card_top = "<div class='card-img'>" + main_img + "</div>" + thumbs_html
        else:
            card_top = "<div class='card-img'>" + EMOJI.get(b['category'],'🏪') + "</div>"
        video_btn = ""
        if b.get('video'):
            video_btn = "<a class='vid' href='" + b.get('video','') + "' target='_blank'>▶️ Watch Video</a>"
        delbtn = ""
        if admin:
            delbtn = "<a class='del' href='/delete/" + str(idx) + "'>×</a>"
        photo_count = ""
        if len(images) > 1:
            photo_count = " 📸 " + str(len(images)) + " photos"
        cards += "<div class='card'>" + delbtn + card_top + "<div class='card-body'>" + feat + new_badge + "<span class='badge'>" + b['category'] + "</span> <span class='badge badge-city'>📍 " + b.get('city','Lilongwe') + "</span><h3>" + b['name'] + "</h3><p>" + b['desc'] + "</p><p>📍 " + b['location'] + "<br><span class='price'>" + b['price'] + "</span><small>" + photo_count + "</small></p>" + video_btn + "<a class='wa' href='https://wa.me/" + b['phone'] + "?text=" + wa_text + "' target='_blank'>💬 Order on WhatsApp</a><a class='update' href='/edit/" + str(idx) + "'>🔄 Update Stock / Edit</a></div></div>"
    if not cards: cards="<p style='grid-column:1/-1; text-align:center;'>No businesses found in this city. Try another city.</p>"
    cat_links=""
    for c in CATEGORIES:
        active = "active" if c==cat else ""
        cat_links += "<a class='" + active + "' href='/?cat=" + c + "&city=" + city + "'>" + c + "</a>"
    city_links=""
    for c in CITIES:
        active = "city-active" if c==city else ""
        city_links += "<a class='" + active + "' href='/?city=" + c + "&cat=" + cat + "'>📍 " + c + "</a>"
    qval = request.args.get('q','')
    city_opts=""
    for c in CITIES:
        if c != 'All':
            sel = "selected" if c==city else ""
            city_opts += "<option " + sel + ">" + c + "</option>"
    cat_opts=""
    for c in CATEGORIES:
        if c != 'All':
            sel = "selected" if c==cat else ""
            cat_opts += "<option " + sel + ">" + c + "</option>"
    return render_template_string(STYLE + "<header><h1>🌍 Bizworld</h1><p>Find the best businesses in Malawi. Order on WhatsApp.</p><a href='/add'>+ Add Your Business - FREE</a><a class='gold' href='/featured'>⭐ Promote My Business</a><br><a class='install' href='#' onclick='installApp(); return false;'>📱 Install Bizworld App</a></header><div id='installBanner' class='install-banner'>📱 Install Bizworld App on your phone for faster shopping! <button onclick='installApp()'>Install Now</button></div><form class='search' method='get' action='/'><input name='q' placeholder='Search e.g. food, salon, phone repair...' value='" + qval + "'><select name='city'><option>All</option>" + city_opts + "</select><select name='cat'><option>All</option>" + cat_opts + "</select><button>Search</button></form><div class='cats'>" + city_links + "</div><div class='cats'>" + cat_links + "</div><div class='grid'>" + cards + "</div><footer>Bizworld • Malawi 🇲🇼 • Lilongwe | Blantyre | Mzuzu | Zomba • <a href='/?admin=1'>Admin</a></footer>")

def process_images(req):
    images = []
    files = req.files.getlist('photos')
    for file in files[:4]:
        if file and file.filename != "":
            data = file.read()
            if len(data) < 1500000:
                mime = file.mimetype or "image/jpeg"
                b64 = base64.b64encode(data).decode('utf-8')
                images.append("data:" + mime + ";base64," + b64)
    link = req.form.get('image','').strip()
    if not images and link:
        images = [link]
    return images

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method=='POST':
        images = process_images(request)
        phone_clean = request.form.get('phone').replace('+','').replace(' ','')
        BUSINESSES.insert(0, {"name": request.form.get('name'), "category": request.form.get('category'), "city": request.form.get('city'), "desc": request.form.get('desc'), "price": request.form.get('price'), "phone": phone_clean, "location": request.form.get('location'), "featured": False, "images": images, "video": request.form.get('video','').strip(), "updated": time.time()})
        save(BUSINESSES); return redirect(url_for('home'))
    return render_template_string(STYLE + """
    <header><h1>+ Add Your Business</h1><p>Join Bizworld Malawi - get customers on WhatsApp</p></header>
    <form class='form' method='post' enctype='multipart/form-data'>
    <input name='name' placeholder='Business Name' required>
    <select name='city'><option>Lilongwe</option><option>Blantyre</option><option>Mzuzu</option><option>Zomba</option><option>Mzimba</option><option>Other</option></select>
    <select name='category'><option>Food</option><option>Fashion</option><option>Beauty</option><option>Phones</option><option>Services</option></select>
    <textarea name='desc' placeholder='What do you sell? e.g. Perfumes - Oud, Vanilla, Rose, Musk. From K15,000 each' required></textarea>
    <input name='price' placeholder='Starting Price e.g. From K15,000' required>
    <input name='phone' placeholder='WhatsApp Number e.g. 265880123456 - YOUR number' required>
    <input name='location' placeholder='Location e.g. Chileka, Blantyre' required>
    <label>📸 Photos - UP TO 4 PHOTOS</label>
    <input type='file' name='photos' accept='image/*' multiple>
    <small>Tip: 1 Business can have MANY cards! Add each new perfume as its OWN card to sell more.</small>
    <label>🎥 Video Link (optional)</label>
    <input name='video' placeholder='Paste TikTok / YouTube link'>
    <input name='image' placeholder='OR paste 1 Photo Link (optional)'>
    <button>Publish My Business →</button></form><p style='text-align:center;'><a href='/'>← Back to Home</a></p>""")

@app.route('/edit/<int:idx>', methods=['GET','POST'])
def edit(idx):
    if idx >= len(BUSINESSES): return redirect('/')
    b = BUSINESSES[idx]
    if request.method=='POST':
        entered = request.form.get('verify_phone','').replace('+','').replace(' ','')
        if entered != b['phone'] and request.form.get('pin','') != ADMIN_PIN:
            return "<h2 style='text-align:center;'>❌ Wrong WhatsApp number. Only the owner can edit this.<br><a href='/'>Back</a></h2>"
        b['name'] = request.form.get('name')
        b['category'] = request.form.get('category')
        b['city'] = request.form.get('city')
        b['desc'] = request.form.get('desc')
        b['price'] = request.form.get('price')
        b['location'] = request.form.get('location')
        b['video'] = request.form.get('video','').strip()
        new_images = process_images(request)
        if new_images:
            b['images'] = new_images
        b['updated'] = time.time()
        save(BUSINESSES); return redirect(url_for('home'))
    sel_city = {}
    for c in ["Lilongwe","Blantyre","Mzuzu","Zomba","Mzimba"]:
        sel_city[c] = "selected" if b.get('city')==c else ""
    sel_cat = {}
    for c in ["Food","Fashion","Beauty","Phones","Services"]:
        sel_cat[c] = "selected" if b['category']==c else ""
    html = STYLE + "<header><h1>🔄 Update Stock - " + b['name'] + "</h1><p>Got new stock? Update here - your card will show 🆕 NEW STOCK and move to top!</p></header>"
    html += "<form class='form' method='post' enctype='multipart/form-data'>"
    html += "<label>Verify - Enter YOUR WhatsApp number (same as when you registered)</label>"
    html += "<input name='verify_phone' placeholder='e.g. " + b['phone'] + "' required>"
    html += "<small>OR enter Admin PIN if you are the owner of Bizworld.</small>"
    html += "<input name='pin' type='password' placeholder='Admin PIN (owner only, optional)'>"
    html += "<label>Business Name</label><input name='name' value='" + b['name'] + "' required>"
    html += "<label>City</label><select name='city'><option " + sel_city["Lilongwe"] + ">Lilongwe</option><option " + sel_city["Blantyre"] + ">Blantyre</option><option " + sel_city["Mzuzu"] + ">Mzuzu</option><option " + sel_city["Zomba"] + ">Zomba</option><option " + sel_city["Mzimba"] + ">Mzimba</option><option>Other</option></select>"
    html += "<label>Category</label><select name='category'><option " + sel_cat["Food"] + ">Food</option><option " + sel_cat["Fashion"] + ">Fashion</option><option " + sel_cat["Beauty"] + ">Beauty</option><option " + sel_cat["Phones"] + ">Phones</option><option " + sel_cat["Services"] + ">Services</option></select>"
    html += "<label>What do you sell NOW? - Write your NEW stock here</label><textarea name='desc' required>" + b['desc'] + "</textarea>"
    html += "<label>Price</label><input name='price' value='" + b['price'] + "' required>"
    html += "<label>Location</label><input name='location' value='" + b['location'] + "' required>"
    html += "<label>📸 NEW Photos - Upload new s
