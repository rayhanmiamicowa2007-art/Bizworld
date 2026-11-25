from flask import Flask, request, render_template_string, redirect, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3, os, uuid

app = Flask(__name__)
app.secret_key = "bizworld-secret-change-this-123"
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# >>> PUT YOUR OWN PASSWORD HERE <<<
ADMIN_PASSWORD = "1995"

# YOUR WHATSAPP FOR PROMOTION
OWNER_WHATSAPP = "265986765421"
PROMOTION_PRICE = "MK5,000 for 7 days"

ALLOWED_IMG = {"png","jpg","jpeg","webp","gif"}
ALLOWED_VIDEO = {"mp4","mov","webm","3gp"}

DISTRICTS = ["Blantyre","Lilongwe","Mzuzu","Zomba","Kasungu","Mangochi","Karonga","Salima","Dedza","Other"]
CATEGORIES = ["Salon & Cosmetics","Electronics & Phones","Food","Fashion & Clothes","Phones & Accessories","Grocery & Shops","Services","Other"]

# Auto product photos - so every card has a beautiful picture
CATEGORY_PHOTOS = {
    "Salon & Cosmetics": "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800&q=80",
    "Electronics & Phones": "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=800&q=80",
    "Food": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80",
    "Fashion & Clothes": "https://images.unsplash.com/photo-1445205170230-053b83016050?w=800&q=80",
    "Phones & Accessories": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&q=80",
    "Grocery & Shops": "https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=800&q=80",
    "Services": "https://images.unsplash.com/photo-1521791136064-7986c2920216?w=800&q=80",
    "Other": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&q=80",
}

def db():
    con = sqlite3.connect("bizworld.db")
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.execute("""
    CREATE TABLE IF NOT EXISTS businesses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        district TEXT NOT NULL,
        town TEXT NOT NULL,
        phone TEXT NOT NULL,
        whatsapp TEXT NOT NULL,
        description TEXT NOT NULL,
        products TEXT,
        photo TEXT,
        video TEXT,
        promoted INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    con.commit()
    count = con.execute("SELECT COUNT(*) FROM businesses").fetchone()[0]
    if count == 0:
        seed = [
            ("Meruna Salon and Cosmetics","Salon & Cosmetics","Blantyre","Chileka","0993066515","265993066515","Salon, hair, nails and cosmetics in Chileka.","Hair • Nails • Cosmetics","","",1),
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
    if p.startswith("0"):
        return "265" + p[1:]
    return p

def save_file(file, allowed):
    if not file or file.filename == "":
        return ""
    ext = file.filename.rsplit(".",1)[-1].lower()
    if ext not in allowed:
        return ""
    name = f"{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], name))
    return name

BASE_CSS = """
<style>
*{box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;margin:0;padding:0;background:#F6F7F9;color:#111;padding-bottom:80px}
.topbar{background:#000;color:#fff;padding:14px 16px 16px;position:sticky;top:0;z-index:10}
.topbar h1{margin:0;font-size:22px;letter-spacing:-0.5px}
.topbar h1 span{color:#FFD700}
.topbar p{margin:4px 0 0;font-size:13px;opacity:0.8}
.search-box{background:#fff;margin:12px 16px 0;padding:4px;border-radius:14px;display:flex;box-shadow:0 2px 10px #0001}
.search-box input{border:none;outline:none;flex:1;padding:12px;font-size:15px;border-radius:14px}
.search-box button{background:#000;color:#fff;border:none;padding:10px 16px;border-radius:10px;font-weight:bold}
.promo-banner{margin:14px 16px;background:linear-gradient(135deg,#FFD700,#FFB800);padding:16px;border-radius:16px;display:flex;justify-content:space-between;align-items:center}
.promo-banner b{font-size:15px}
.promo-banner p{margin:4px 0 0;font-size:12px}
.promo-banner a{background:#000;color:#fff;padding:10px 14px;border-radius:10px;text-decoration:none;font-size:13px;font-weight:bold;white-space:nowrap}
.add-btn{display:block;margin:0 16px;background:#25D366;color:#fff;text-align:center;padding:14px;border-radius:14px;text-decoration:none;font-weight:bold;font-size:15px;box-shadow:0 4px 12px #25D36644}
.section{padding:14px 16px 0}
.section h3{margin:0 0 10px;font-size:16px}
.chips{display:flex;gap:8px;overflow-x:auto;padding-bottom:4px;scrollbar-width:none}
.chips a{white-space:nowrap;padding:8px 14px;background:#fff;border:1px solid #eee;border-radius:20px;text-decoration:none;color:#111;font-size:13px;font-weight:600}
.chips a.active{background:#000;color:#fff;border-color:#000}
.card{background:#fff;border-radius:18px;margin:12px 16px 0;padding:0;overflow:hidden;box-shadow:0 2px 12px #0001}
.card.promoted{border:2px solid #FFD700}
.card-img{width:100%;height:190px;object-fit:cover;background:#eee;display:block}
.card-body{padding:14px}
.badge{display:inline-block;background:#FFD700;padding:4px 8px;border-radius:6px;font-size:11px;font-weight:bold;margin-bottom:8px}
.badge-green{display:inline-block;background:#E6F7ED;color:#0A7A3A;padding:4px 8px;border-radius:6px;font-size:11px;font-weight:bold}
.card-body h2{margin:0 0 4px;font-size:18px}
.card-body .meta{font-size:13px;color:#666;margin:0}
.card-body .desc{font-size:14px;line-height:1.5;color:#333;margin:10px 0 6px}
.card-body .prod{font-size:13px;color:#111;background:#F6F7F9;padding:8px 10px;border-radius:10px}
.actions{display:flex;gap:8px;margin-top:12px}
.actions a{flex:1;text-align:center;padding:12px;border-radius:12px;text-decoration:none;font-weight:bold;font-size:14px}
.btn-wa{background:#25D366;color:#fff}
.btn-promote{background:#FFD700;color:#000}
.admin-row{display:flex;gap:8px;margin-top:10px}
.admin-row a{flex:1;text-align:center;padding:9px;border-radius:10px;text-decoration:none;font-size:13px;font-weight:bold}
.btn-red{background:#FFEAEA;color:#D00}
.btn-gold{background:#FFF4CC;color:#000}
.bottom-nav{position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid #eee;display:flex;justify-content:space-around;padding:10px 0 14px;z-index:20}
.bottom-nav a{text-decoration:none;color:#666;text-align:center;font-size:11px}
.bottom-nav a.active{color:#000;font-weight:bold}
.bottom-nav span{font-size:20px;display:block}
input,select,textarea{width:100%;padding:13px;margin:7px 0;border-radius:12px;border:1px solid #ddd;font-size:15px;background:#fff}
button.submit{width:100%;padding:15px;background:#25D366;color:#fff;border:none;border-radius:14px;font-weight:bold;font-size:16px}
</style>
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#000000">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Bizworld">
<link rel="apple-touch-icon" href="/icon-192.png">
"""

HOME = BASE_CSS + """
<div class="topbar">
<h1>Bizworld <span>🇲🇼</span></h1>
<p>{{count}} real businesses • Blantyre • Lilongwe • Mzuzu</p>
</div>

<button id="installBtn" style="display:none;margin:12px 16px 0;width:calc(100% - 32px);background:#000;color:#fff;padding:13px;border-radius:14px;border:none;font-weight:bold">📲 Install Bizworld App</button>
<script>
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); deferredPrompt = e; document.getElementById('installBtn').style.display='block'; });
document.getElementById('installBtn')?.addEventListener('click', async () => { if(deferredPrompt){ deferredPrompt.prompt(); await deferredPrompt.userChoice; deferredPrompt=null; } });
if ('serviceWorker' in navigator) { navigator.serviceWorker.register('/sw.js'); }
</script>

<form method="GET" action="/" class="search-box">
<input type="text" name="q" value="{{q}}" placeholder="🔍 Search salon, pizza, iPhone...">
<input type="hidden" name="pw" value="{{pw}}">
<button type="submit">Search</button>
</form>

<div class="promo-banner">
<div><b>⭐ Be #1 on Bizworld</b><p>Promotion: {{promotion_price}}</p></div>
<a href="https://wa.me/{{owner_whatsapp}}?text=Hi Bizworld, I want to PROMOTE my business." target="_blank">Promote →</a>
</div>

<a class="add-btn" href="/add">+ Add Your Business — FREE</a>

<div class="section"><h3>📍 District</h3><div class="chips">
{% for d in districts %}<a href="/?district={{d}}&category={{cat}}&q={{q}}&pw={{pw}}" class="{{'active' if d==district else ''}}">{{d}}</a>{% endfor %}
</div></div>

<div class="section"><h3>🛍️ Category</h3><div class="chips">
{% for c in categories %}<a href="/?district={{district}}&category={{c}}&q={{q}}&pw={{pw}}" class="{{'active' if c==cat else ''}}">{{c}}</a>{% endfor %}
</div></div>

{% for b in businesses %}
<div class="card {{'promoted' if b['promoted'] else ''}}">
{% if b['photo'] %}
<img class="card-img" src="/uploads/{{b['photo']}}">
{% else %}
<img class="card-img" src="{{category_photos.get(b['category'], category_photos['Other'])}}">
{% endif %}
{% if b['video'] %}<video controls src="/uploads/{{b['video']}}" style="width:100%"></video>{% endif %}
<div class="card-body">
{% if b['promoted'] %}<span class="badge">⭐ PROMOTED • FEATURED</span> {% else %}<span class="badge-green">✓ VERIFIED BUSINESS</span>{% endif %}
<h2>{{b['name']}}</h2>
<p class="meta">{{b['category']}} • 📍 {{b['town']}}, {{b['district']}}</p>
<p class="desc">{{b['description']}}</p>
<div class="prod">{{b['products']}}</div>
<div class="actions">
<a class="btn-wa" href="https://wa.me/{{b['whatsapp']}}?text=Hi, I found you on Bizworld. I want to order." target="_blank">💬 WhatsApp</a>
<a class="btn-promote" href="https://wa.me/{{owner_whatsapp}}?text=Hi Bizworld, I want to PROMOTE my business {{b['name']}}." target="_blank">⭐ Promote Me</a>
</div>
{% if is_admin %}<div class="admin-row">
<a class="btn-red" href="/delete/{{b['id']}}?pw={{pw}}">🗑 Remove</a>
<a class="btn-gold" href="/promote/{{b['id']}}?pw={{pw}}">{{'Unpromote' if b['promoted'] else '⭐ Promote'}}</a>
</div>{% endif %}
</div></div>
{% else %}<p style="text-align:center;padding:20px">No businesses found.</p>{% endfor %}

<div class="bottom-nav">
<a href="/" class="active"><span>🏠</span>Home</a>
<a href="/?category=Salon & Cosmetics"><span>💇</span>Salon</a>
<a href="/?category=Food"><span>🍔</span>Food</a>
<a href="/add"><span>➕</span>Add</a>
<a href="https://wa.me/{{owner_whatsapp}}"><span>💬</span>Help</a>
</div>
"""

ADD = BASE_CSS + """
<div class="topbar"><h1>+ Add Business</h1><p>It will appear immediately</p></div>
<div style="padding:16px">
<form method="POST" enctype="multipart/form-data">
<input name="name" placeholder="Business Name" required>
<select name="category" required>{% for c in categories %}<option>{{c}}</option>{% endfor %}</select>
<select name="district" required>{% for d in districts %}<option>{{d}}</option>{% endfor %}</select>
<input name="town" placeholder="Town / Area e.g Chileka" required>
<input name="phone" placeholder="WhatsApp Number e.g 0993066515" required>
<textarea name="description" placeholder="What do you sell?" required></textarea>
<input name="products" placeholder="Products e.g Hair, Nails, Cosmetics">
<label><b>📸 Business Photo</b></label><input type="file" name="photo" accept="image/*">
<label><b>🎥 Business Video (max 50MB)</b></label><input type="file" name="video" accept="video/*">
<button class="submit" type="submit">ADD MY BUSINESS ✅</button>
</form><br><a href="/">← Back</a>
</div>
"""

@app.route("/")
def home():
    district = request.args.get("district","All")
    cat = request.args.get("category","All")
    q = request.args.get("q","").strip()
    pw = request.args.get("pw","")
    is_admin = (pw == ADMIN_PASSWORD)
    con = db()
    sql = "SELECT * FROM businesses WHERE 1=1"
    params = []
    if district != "All":
        sql += " AND district=?"; params.append(district)
    if cat != "All":
        sql += " AND category=?"; params.append(cat)
    if q:
        sql += " AND (name LIKE ? OR description LIKE ? OR products LIKE ? OR town LIKE ?)"
        like = f"%{q}%"; params += [like,like,like,like]
    sql += " ORDER BY promoted DESC, created_at DESC"
    rows = con.execute(sql, params).fetchall()
    con.close()
    from flask import render_template_string as r
    return r(HOME, businesses=rows, count=len(rows), category_photos=CATEGORY_PHOTOS, districts=["All"]+DISTRICTS, categories=["All"]+CATEGORIES, district=district, cat=cat, q=q, pw=pw, is_admin=is_admin, owner_whatsapp=OWNER_WHATSAPP, promotion_price=PROMOTION_PRICE)

@app.route("/add", methods=["GET","POST"])
def add():
    from flask import render_template_string as r
    if request.method == "POST":
        photo = save_file(request.files.get("photo"), ALLOWED_IMG)
        video = save_file(request.files.get("video"), ALLOWED_VIDEO)
        phone = request.form["phone"]
        con = db()
        con.execute("INSERT INTO businesses (name,category,district,town,phone,whatsapp,description,products,photo,video) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (request.form["name"], request.form["category"], request.form["district"], request.form["town"], phone, to_whatsapp(phone), request.form["description"], request.form["products"], photo, video))
        con.commit(); con.close()
        return redirect("/")
    return r(ADD, categories=CATEGORIES, districts=DISTRICTS)

@app.route("/delete/<int:bid>")
def delete(bid):
    if request.args.get("pw") != ADMIN_PASSWORD:
        return "Wrong password. Only owner can delete."
    con = db(); con.execute("DELETE FROM businesses WHERE id=?", (bid,)); con.commit(); con.close()
    return redirect(f"/?pw={ADMIN_PASSWORD}")

@app.route("/promote/<int:bid>")
def promote(bid):
    if request.args.get("pw") != ADMIN_PASSWORD:
        return "Wrong password."
    con = db()
    cur = con.execute("SELECT promoted FROM businesses WHERE id=?", (bid,)).fetchone()
    if cur:
        con.execute("UPDATE businesses SET promoted=? WHERE id=?", (0 if cur[0] else 1, bid))
        con.commit()
    con.close()
    return redirect(f"/?pw={ADMIN_PASSWORD}")

@app.route("/uploads/<name>")
def uploaded(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route("/manifest.json")
def manifest():
    return send_from_directory(".", "manifest.json", mimetype="application/manifest+json")

@app.route("/sw.js")
def sw():
    return send_from_directory(".", "sw.js", mimetype="application/javascript")

@app.route("/icon-192.png")
def icon192():
    return send_from_directory(".", "icon-192.png")

@app.route("/icon-512.png")
def icon512():
    return send_from_directory(".", "icon-512.png")

if __name__ == "__main__":
    app.run(debug=True)
