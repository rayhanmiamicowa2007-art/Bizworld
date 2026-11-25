from flask import Flask, request, render_template_string, redirect, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3, os, uuid, json

app = Flask(__name__)
app.secret_key = "bizworld-secret-change-this-123"
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# >>> PUT YOUR OWN PASSWORD HERE <<<
ADMIN_PASSWORD = "1995"
OWNER_WHATSAPP = "265986765421"
PROMOTION_PRICE = "MK5,000 for 7 days"

ALLOWED_IMG = {"png","jpg","jpeg","webp","gif"}
ALLOWED_VIDEO = {"mp4","mov","webm","3gp"}

DISTRICTS = ["Blantyre","Lilongwe","Mzuzu","Zomba","Mzimba","Kasungu","Mangochi","Karonga","Salima","Dedza","Other"]
CATEGORIES = ["Salon & Cosmetics","Electronics & Phones","Food","Fashion & Clothes","Phones & Accessories","Grocery & Shops","Services","Other"]
CAT_SHORT = {"Salon & Cosmetics":"Beauty","Electronics & Phones":"Electronics","Food":"Food","Fashion & Clothes":"Fashion","Phones & Accessories":"Phones","Grocery & Shops":"Grocery","Services":"Services","Other":"Other"}

CATEGORY_PHOTOS = {
    "Salon & Cosmetics": ["https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800&q=80","https://images.unsplash.com/photo-1522337660859-02fbefca4702?w=200&q=60","https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?w=200&q=60","https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=200&q=60","https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=200&q=60"],
    "Electronics & Phones": ["https://images.unsplash.com/photo-1498049794561-7780e7231661?w=800&q=80","https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=200&q=60","https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=200&q=60","https://images.unsplash.com/photo-1588508065123-287b28e013da?w=200&q=60","https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=200&q=60"],
    "Food": ["https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80","https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=200&q=60","https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=200&q=60","https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=200&q=60","https://images.unsplash.com/photo-1550547660-d9450f859349?w=200&q=60"],
    "Fashion & Clothes": ["https://images.unsplash.com/photo-1445205170230-053b83016050?w=800&q=80","https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=200&q=60","https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=200&q=60","https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=200&q=60","https://images.unsplash.com/photo-1483985988355-763728e1935b?w=200&q=60"],
    "Phones & Accessories": ["https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&q=80","https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=200&q=60","https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=200&q=60","https://images.unsplash.com/photo-1580910051074-3eb694886505?w=200&q=60","https://images.unsplash.com/photo-1605236453806-6ff368512f6e?w=200&q=60"],
    "Grocery & Shops": ["https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=800&q=80","https://images.unsplash.com/photo-1542838132-92c53300491e?w=200&q=60","https://images.unsplash.com/photo-1588964895597-cfccd6e2dbf9?w=200&q=60","https://images.unsplash.com/photo-1583258292688-d0213dc5a3a8?w=200&q=60","https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=200&q=60"],
    "Services": ["https://images.unsplash.com/photo-1521791136064-7986c2920216?w=800&q=80","https://images.unsplash.com/photo-1556761175-b413da4baf72?w=200&q=60","https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=200&q=60","https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=200&q=60","https://images.unsplash.com/photo-1521791136064-7986c2920216?w=200&q=60"],
    "Other": ["https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&q=80","https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=200&q=60","https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=200&q=60","https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=200&q=60","https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=200&q=60"],
}

def db():
    con = sqlite3.connect("bizworld.db"); con.row_factory = sqlite3.Row; return con

def init_db():
    con = db()
    con.execute("""CREATE TABLE IF NOT EXISTS businesses (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT NOT NULL,
        district TEXT NOT NULL, town TEXT NOT NULL, phone TEXT NOT NULL, whatsapp TEXT NOT NULL,
        description TEXT NOT NULL, products TEXT, photo TEXT, video TEXT,
        photos TEXT DEFAULT '[]', promoted INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    # Add photos column if old DB exists
    try: con.execute("ALTER TABLE businesses ADD COLUMN photos TEXT DEFAULT '[]'")
    except: pass
    con.commit()
    count = con.execute("SELECT COUNT(*) FROM businesses").fetchone()[0]
    if count == 0:
        seed = [
            ("Meruna salon and cosmetics","Salon & Cosmetics","Blantyre","Chileka","0993066515","265993066515","We sell cosmetics and we are doing salon","Hair • Nails • Cosmetics","","",1),
            ("Wow Skin Care Malawi","Salon & Cosmetics","Blantyre","Mandala","0887616804","265887616804","Original skincare & hair care. Nationwide delivery.","Skincare • Hair care","","",0),
            ("The MLKY Bar","Salon & Cosmetics","Blantyre","Ginnery Corner","0999504369","265999504369","Lashes, hair, nails, facials, laser.","Lashes • Hair • Nails","","",0),
            ("Beyond Elegance Cosmetics","Salon & Cosmetics","Lilongwe","Olympic Mall","0993924859","265993924859","Makeup & cosmetics. Nationwide delivery.","Makeup • Foundation","","",0),
            ("Fatha Hi-Tech","Electronics & Phones","Lilongwe","City Centre","0999621027","265999621027","Laptops, printers, monitors. Also Blantyre MPICO.","Laptops • Printers • Monitors","","",0),
            ("Kips Restaurant","Food","Blantyre","Blantyre City","0883999999","265883999999","Restaurant & ice cream. FREE delivery.","Pizza • Burgers • Ice Cream","","",0),
            ("Zeena's Kitchen","Food","Lilongwe","Lilongwe","0889785323","265889785323","Lunch delivery to office. Wraps, meal prep.","Wraps • Meal Prep","","",0),
            ("Cherries Collection","Fashion & Clothes","Mzuzu","Mzuzu City","0993185015","265993185015","Women's dresses MK30k-35k.","Dresses • Maxi Dresses","","",0),
            ("Aroma Avenue","Salon & Cosmetics","Zomba","Zomba City","0994002792","265994002792","Perfume, Avon, Justine, Dove.","Perfume • Avon • Justine","","",0),
            ("Rororea Glow and Essentials","Salon & Cosmetics","Mzuzu","Luwinga","0896040032","265896040032","Foundations, lotions, soaps.","Foundation • CeraVe • Nivea","","",0),
        ]
        con.executemany("INSERT INTO businesses (name,category,district,town,phone,whatsapp,description,products,photo,video,promoted) VALUES (?,?,?,?,?,?,?,?,?,?,?)", seed)
        con.commit()
    con.close()
init_db()

def to_whatsapp(phone):
    p = phone.strip().replace(" ","").replace("+","").replace("-","")
    if p.startswith("0"): return "265" + p[1:]
    return p

def save_file(file, allowed):
    if not file or file.filename == "": return ""
    ext = file.filename.rsplit(".",1)[-1].lower()
    if ext not in allowed: return ""
    name = f"{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], name))
    return name

def get_photos(b):
    # Returns list of photo URLs for a business
    try:
        pics = json.loads(b['photos'] or '[]')
    except: pics = []
    if pics:
        return [f"/uploads/{p}" for p in pics]
    if b['photo']:
        return [f"/uploads/{b['photo']}"]
    return CATEGORY_PHOTOS.get(b['category'], CATEGORY_PHOTOS['Other'])

BASE_CSS = """
<style>
*{box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;margin:0;padding:0;background:#F2F3F5;color:#111}
.header{background:#0B1D3A;color:#fff;text-align:center;padding:16px 12px 18px}
.header h1{margin:0;font-size:24px}
.header p{margin:4px 0 12px;font-size:12px;opacity:0.85}
.btn-green{background:#25D366;color:#fff;border:none;padding:9px 14px;border-radius:20px;font-weight:bold;font-size:12px;text-decoration:none;display:inline-block}
.btn-yellow{background:#FFC107;color:#000;border:none;padding:9px 14px;border-radius:20px;font-weight:bold;font-size:12px;text-decoration:none;display:inline-block}
.search-wrap{background:#fff;margin:-2px 10px 0;padding:8px;border-radius:12px;display:flex;gap:6px;box-shadow:0 2px 8px #0002}
.search-wrap input{flex:1;border:1px solid #eee;border-radius:8px;padding:10px;font-size:13px;outline:none}
.search-wrap select{border:1px solid #eee;border-radius:8px;padding:8px;font-size:12px;background:#fff}
.search-wrap button{background:#000;color:#fff;border:none;border-radius:8px;padding:10px 12px;font-weight:bold;font-size:12px}
.chips{display:flex;gap:6px;overflow-x:auto;padding:10px 10px 0;scrollbar-width:none}
.chips a{white-space:nowrap;padding:7px 11px;background:#fff;border-radius:20px;text-decoration:none;color:#111;font-size:12px;font-weight:500;box-shadow:0 1px 3px #0001}
.chips a.active{background:#0B3D2E;color:#fff}
.chips2{display:flex;gap:6px;overflow-x:auto;padding:8px 10px 0;scrollbar-width:none}
.chips2 a{white-space:nowrap;padding:7px 12px;background:#111;color:#fff;border-radius:20px;text-decoration:none;font-size:12px;font-weight:600}
.chips2 a.light{background:#fff;color:#111;box-shadow:0 1px 3px #0001}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:12px 10px 30px}
.card{background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 2px 8px #0001;display:flex;flex-direction:column}
.card.promoted{border:2px solid #FFD700}
.card-img{width:100%;height:150px;object-fit:cover;display:block}
.thumbs{display:flex;gap:4px;padding:6px 8px 0}
.thumbs img{width:32px;height:32px;object-fit:cover;border-radius:6px;border:1px solid #eee;cursor:pointer}
.card-body{padding:8px 10px 10px;flex:1;display:flex;flex-direction:column}
.badges{display:flex;gap:4px;flex-wrap:wrap;margin-bottom:6px}
.badge{font-size:10px;font-weight:bold;padding:3px 6px;border-radius:10px}
.badge-new{background:#E6F7ED;color:#0A7A3A}
.badge-cat{background:#EAF2FF;color:#1A5CFF}
.badge-loc{background:#EAF7EA;color:#0A7A3A}
.card-body h3{margin:0;font-size:13px;line-height:1.3}
.card-body .desc{font-size:11px;color:#666;line-height:1.4;margin:5px 0}
.card-body .loc{font-size:11px;color:#333;margin:0}
.price{font-size:12px;color:#0A7A3A;font-weight:bold;margin:3px 0 8px}
.btn-wa{background:#25D366;color:#fff;text-align:center;padding:10px;border-radius:8px;text-decoration:none;font-weight:bold;font-size:12px}
.btn-edit{background:#fff;color:#111;border:1px solid #eee;text-align:center;padding:9px;border-radius:8px;text-decoration:none;font-size:11px;margin-top:6px;display:block}
.footer{text-align:center;font-size:11px;color:#888;padding:10px}
input,select,textarea{width:100%;padding:13px;margin:7px 0;border-radius:12px;border:1px solid #ddd;font-size:15px;background:#fff}
button.submit{width:100%;padding:15px;background:#25D366;color:#fff;border:none;border-radius:14px;font-weight:bold;font-size:16px}
.preview{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0}
.preview img,.preview video{width:80px;height:80px;object-fit:cover;border-radius:10px}
</style>
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#0B1D3A">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Bizworld">
<link rel="apple-touch-icon" href="/icon-192.png">
"""

HOME = BASE_CSS + """
<div class="header">
<h1>🌍 Bizworld</h1>
<p>Find the best businesses in Malawi. Order on WhatsApp.</p>
<a class="btn-green" href="/add">+ Add Your Business - FREE</a>
<a class="btn-yellow" href="https://wa.me/{{owner_whatsapp}}?text=Hi Bizworld, I want to PROMOTE my business." target="_blank">⭐ Promote My Business</a>
</div>
<button id="installBtn" style="display:none;margin:10px;width:calc(100% - 20px);background:#000;color:#fff;padding:12px;border-radius:12px;border:none;font-weight:bold">📲 Install Bizworld App</button>
<script>
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); deferredPrompt = e; document.getElementById('installBtn').style.display='block'; });
document.getElementById('installBtn')?.addEventListener('click', async () => { if(deferredPrompt){ deferredPrompt.prompt(); await deferredPrompt.userChoice; deferredPrompt=null; } });
if ('serviceWorker' in navigator) { navigator.serviceWorker.register('/sw.js'); }
function changeImg(id, src){ document.getElementById('main-'+id).src = src; }
</script>
<form method="GET" action="/" class="search-wrap">
<input type="text" name="q" value="{{q}}" placeholder="Search e.g. food, salon, phone repair...">
<input type="hidden" name="pw" value="{{pw}}">
<select name="district"><option value="All">All</option>{% for d in districts %}{% if d != 'All' %}<option value="{{d}}" {{'selected' if d==district}}>{{d}}</option>{% endif %}{% endfor %}</select>
<select name="category"><option value="All">All</option>{% for c in categories %}{% if c != 'All' %}<option value="{{c}}" {{'selected' if c==cat}}>{{cat_short.get(c,c)}}</option>{% endif %}{% endfor %}</select>
<button type="submit">Search</button>
</form>
<div class="chips">{% for d in districts %}<a href="/?district={{d}}&category={{cat}}&q={{q}}&pw={{pw}}" class="{{'active' if d==district else ''}}">📍 {{d}}</a>{% endfor %}</div>
<div class="chips2"><a href="/?district={{district}}&category=All&q={{q}}&pw={{pw}}" class="{{'' if cat != 'All' else ''}}">All</a>{% for c in categories %}{% if c != 'All' %}<a href="/?district={{district}}&category={{c}}&q={{q}}&pw={{pw}}" class="{{'' if c==cat else 'light'}}">{{cat_short.get(c,c)}}</a>{% endif %}{% endfor %}</div>
<div class="grid">
{% for b in businesses %}
<div class="card {{'promoted' if b['promoted'] else ''}}">
<img id="main-{{b['id']}}" class="card-img" src="{{b['photos_list'][0]}}">
{% if b['video'] %}<video controls src="/uploads/{{b['video']}}" style="width:100%;height:130px;background:#000"></video>{% endif %}
<div class="thumbs">{% for t in b['photos_list'][1:5] %}<img src="{{t}}" onclick="changeImg({{b['id']}},'{{t}}')">{% endfor %}</div>
<div class="card-body">
<div class="badges"><span class="badge badge-new">🆕 NEW STOCK!</span><span class="badge badge-cat">{{cat_short.get(b['category'], b['category'])}}</span><span class="badge badge-loc">📍 {{b['district']}}</span>{% if b['promoted'] %}<span class="badge" style="background:#FFD700">⭐ PROMOTED</span>{% endif %}</div>
<h3>{{b['name']}}</h3>
<p class="desc">{{b['description']}}</p>
<p class="loc">📍 {{b['town']}}, {{b['district']}}</p>
<div class="price">📸 {{b['photos_list']|length}} photos {% if b['video'] %} • 🎥 Video{% endif %}</div>
<a class="btn-wa" href="https://wa.me/{{b['whatsapp']}}?text=Hi, I found you on Bizworld. I want to order." target="_blank">💬 Order on WhatsApp</a>
<a class="btn-edit" href="https://wa.me/{{owner_whatsapp}}?text=Hi Bizworld, I want to update {{b['name']}}">🔄 Update Stock / Edit</a>
{% if is_admin %}<div style="display:flex;gap:6px;margin-top:6px"><a class="btn-edit" style="flex:1;background:#FFEAEA;color:#D00" href="/delete/{{b['id']}}?pw={{pw}}">🗑 Remove</a><a class="btn-edit" style="flex:1;background:#FFF4CC" href="/promote/{{b['id']}}?pw={{pw}}">⭐ Promote</a></div>{% endif %}
</div></div>
{% else %}<p style="grid-column:1/-1;text-align:center">No businesses found.</p>{% endfor %}
</div>
<div class="footer">Bizworld • Malawi 🇲🇼 • Lilongwe | Blantyre | Mzuzu | Zomba</div>
"""

ADD = BASE_CSS + """
<div class="header"><h1>+ Add Business</h1><p>Add photos & video - they will appear immediately</p></div>
<div style="padding:16px;background:#fff">
<form method="POST" enctype="multipart/form-data">
<input name="name" placeholder="Business Name" required>
<select name="category" required>{% for c in categories %}<option>{{c}}</option>{% endfor %}</select>
<select name="district" required>{% for d in districts %}<option>{{d}}</option>{% endfor %}</select>
<input name="town" placeholder="Town / Area e.g Chileka" required>
<input name="phone" placeholder="WhatsApp Number e.g 0993066515" required>
<textarea name="description" placeholder="What do you sell?" required></textarea>
<input name="products" placeholder="Products e.g Hair, Nails, Cosmetics">
<label><b>📸 Business Photos (Select up to 5 - Hold to select many)</b></label>
<input type="file" name="photos" accept="image/*" multiple onchange="previewPhotos(this)">
<div id="photoPreview" class="preview"></div>
<script>
function previewPhotos(input){
  var box = document.getElementById('photoPreview'); box.innerHTML='';
  for(var f of input.files){ var r = new FileReader(); r.onload = function(e){ var i=document.createElement('img'); i.src=e.target.result; box.appendChild(i); }; r.readAsDataURL(f); }
}
function previewVideo(input){
  var box = document.getElementById('videoPreview'); box.innerHTML='';
  if(input.files[0]){ var v=document.createElement('video'); v.controls=true; v.src=URL.createObjectURL(input.files[0]); box.appendChild(v); }
}
</script>
<label><b>🎥 Business Video (1 video - max 100MB)</b></label>
<input type="file" name="video" accept="video/*" onchange="previewVideo(this)">
<div id="videoPreview" class="preview"></div>
<button class="submit" type="submit">ADD MY BUSINESS ✅</button>
</form><br><a href="/">← Back</a>
</div>
"""

@app.route("/")
def home():
    district = request.args.get("district","All"); cat = request.args.get("category","All"); q = request.args.get("q","").strip(); pw = request.args.get("pw","")
    is_admin = (pw == ADMIN_PASSWORD)
    con = db(); sql = "SELECT * FROM businesses WHERE 1=1"; params=[]
    if district != "All": sql += " AND district=?"; params.append(district)
    if cat != "All": sql += " AND category=?"; params.append(cat)
    if q:
        sql += " AND (name LIKE ? OR description LIKE ? OR products LIKE ? OR town LIKE ?)"
        like=f"%{q}%"; params += [like,like,like,like]
    sql += " ORDER BY promoted DESC, created_at DESC"
    rows = con.execute(sql, params).fetchall(); con.close()
    # Convert to dict + add photos_list
    biz = []
    for r in rows:
        d = dict(r); d['photos_list'] = get_photos(r); biz.append(d)
    from flask import render_template_string as r
    return r(HOME, businesses=biz, count=len(biz), cat_short=CAT_SHORT, districts=["All"]+DISTRICTS, categories=["All"]+CATEGORIES, district=district, cat=cat, q=q, pw=pw, is_admin=is_admin, owner_whatsapp=OWNER_WHATSAPP, promotion_price=PROMOTION_PRICE)

@app.route("/add", methods=["GET","POST"])
def add():
    from flask import render_template_string as r
    if request.method == "POST":
        # Multiple photos
        photos = []
        for f in request.files.getlist("photos"):
            saved = save_file(f, ALLOWED_IMG)
            if saved: photos.append(saved)
        # Backward compat: old single photo field
        single = save_file(request.files.get("photo"), ALLOWED_IMG)
        if single and not photos: photos = [single]
        video = save_file(request.files.get("video"), ALLOWED_VIDEO)
        phone = request.form["phone"]
        con = db()
        con.execute("INSERT INTO businesses (name,category,district,town,phone,whatsapp,description,products,photo,video,photos) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (request.form["name"], request.form["category"], request.form["district"], request.form["town"], phone, to_whatsapp(phone), request.form["description"], request.form["products"], photos[0] if photos else "", video, json.dumps(photos)))
        con.commi
