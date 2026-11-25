from flask import Flask, request, render_template_string, redirect, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3, os, uuid, json

app = Flask(__name__)
app.secret_key = "bizworld-2026-secret"
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

ADMIN_PASSWORD = "1995"
OWNER_WHATSAPP = "265986765421"

ALLOWED_IMG = {"png", "jpg", "jpeg", "webp", "gif"}
ALLOWED_VIDEO = {"mp4", "mov", "webm", "3gp"}

DISTRICTS = ["Blantyre", "Lilongwe", "Mzuzu", "Zomba", "Mzimba", "Kasungu", "Mangochi", "Karonga", "Salima", "Dedza", "Other"]
CATEGORIES = ["Salon & Cosmetics", "Electronics & Phones", "Food", "Fashion & Clothes", "Phones & Accessories", "Grocery & Shops", "Services", "Other"]
CAT_SHORT = {"Salon & Cosmetics": "Beauty", "Electronics & Phones": "Electronics", "Food": "Food", "Fashion & Clothes": "Fashion", "Phones & Accessories": "Phones", "Grocery & Shops": "Grocery", "Services": "Services", "Other": "Other"}

CATEGORY_PHOTOS = {
    "Salon & Cosmetics": ["https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800&q=80", "https://images.unsplash.com/photo-1522337660859-02fbefca4702?w=200&q=60", "https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?w=200&q=60", "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=200&q=60", "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=200&q=60"],
    "Electronics & Phones": ["https://images.unsplash.com/photo-1498049794561-7780e7231661?w=800&q=80", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=200&q=60", "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=200&q=60", "https://images.unsplash.com/photo-1588508065123-287b28e013da?w=200&q=60", "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=200&q=60"],
    "Food": ["https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80", "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=200&q=60", "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=200&q=60", "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=200&q=60", "https://images.unsplash.com/photo-1550547660-d9450f859349?w=200&q=60"],
    "Fashion & Clothes": ["https://images.unsplash.com/photo-1445205170230-053b83016050?w=800&q=80", "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=200&q=60", "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=200&q=60", "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=200&q=60", "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=200&q=60"],
    "Phones & Accessories": ["https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&q=80", "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=200&q=60", "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=200&q=60", "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=200&q=60", "https://images.unsplash.com/photo-1605236453806-6ff368512f6e?w=200&q=60"],
    "Grocery & Shops": ["https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=800&q=80", "https://images.unsplash.com/photo-1542838132-92c53300491e?w=200&q=60", "https://images.unsplash.com/photo-1588964895597-cfccd6e2dbf9?w=200&q=60", "https://images.unsplash.com/photo-1583258292688-d0213dc5a3a8?w=200&q=60", "https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=200&q=60"],
    "Services": ["https://images.unsplash.com/photo-1521791136064-7986c2920216?w=800&q=80", "https://images.unsplash.com/photo-1556761175-b413da4baf72?w=200&q=60", "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=200&q=60", "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=200&q=60", "https://images.unsplash.com/photo-1521791136064-7986c2920216?w=200&q=60"],
    "Other": ["https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&q=80", "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=200&q=60", "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=200&q=60", "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=200&q=60", "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=200&q=60"],
}

def db():
    con = sqlite3.connect("bizworld.db")
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.execute("CREATE TABLE IF NOT EXISTS businesses (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT NOT NULL, district TEXT NOT NULL, town TEXT NOT NULL, phone TEXT NOT NULL, whatsapp TEXT NOT NULL, description TEXT NOT NULL, products TEXT, photo TEXT, video TEXT, price TEXT DEFAULT '', photos TEXT DEFAULT '[]', promoted INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    try:
        con.execute("ALTER TABLE businesses ADD COLUMN photos TEXT DEFAULT '[]'")
    except:
        pass
    try:
        con.execute("ALTER TABLE businesses ADD COLUMN price TEXT DEFAULT ''")
    except:
        pass
    con.commit()
    count = con.execute("SELECT COUNT(*) FROM businesses").fetchone()[0]
    if count == 0:
        seed = [
            ("Meruna salon and cosmetics", "Salon & Cosmetics", "Blantyre", "Chileka", "0993066515", "265993066515", "We sell cosmetics and we are doing salon", "Hair Nails Cosmetics", "", "", "15000", 1),
            ("Wow Skin Care Malawi", "Salon & Cosmetics", "Blantyre", "Mandala", "0887616804", "265887616804", "Original skincare and hair care. Nationwide delivery.", "Skincare Hair care", "", "", "25000", 0),
            ("The MLKY Bar", "Salon & Cosmetics", "Blantyre", "Ginnery Corner", "0999504369", "265999504369", "Lashes, hair, nails, facials, laser.", "Lashes Hair Nails", "", "", "20000", 0),
            ("Beyond Elegance Cosmetics", "Salon & Cosmetics", "Lilongwe", "Olympic Mall", "0993924859", "265993924859", "Makeup and cosmetics. Nationwide delivery.", "Makeup Foundation", "", "", "18500", 0),
            ("Fatha Hi-Tech", "Electronics & Phones", "Lilongwe", "City Centre", "0999621027", "265999621027", "Laptops, printers, monitors. Also Blantyre MPICO.", "Laptops Printers Monitors", "", "", "850000", 0),
            ("Kips Restaurant", "Food", "Blantyre", "Blantyre City", "0883999999", "265883999999", "Restaurant and ice cream. FREE delivery.", "Pizza Burgers Ice Cream", "", "", "12000", 0),
            ("Zeena Kitchen", "Food", "Lilongwe", "Lilongwe", "0889785323", "265889785323", "Lunch delivery to office. Wraps, meal prep.", "Wraps Meal Prep", "", "", "8500", 0),
            ("Cherries Collection", "Fashion & Clothes", "Mzuzu", "Mzuzu City", "0993185015", "265993185015", "Womens dresses MK30k-35k.", "Dresses Maxi Dresses", "", "", "32000", 0),
            ("Aroma Avenue", "Salon & Cosmetics", "Zomba", "Zomba City", "0994002792", "265994002792", "Perfume, Avon, Justine, Dove.", "Perfume Avon Justine", "", "", "22000", 0),
            ("Rororea Glow", "Salon & Cosmetics", "Mzuzu", "Luwinga", "0896040032", "265896040032", "Foundations, lotions, soaps.", "Foundation CeraVe Nivea", "", "", "16000", 0),
        ]
        con.executemany("INSERT INTO businesses (name,category,district,town,phone,whatsapp,description,products,photo,video,price,promoted) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", seed)
        con.commit()
    con.close()

init_db()

def to_whatsapp(phone):
    p = phone.strip().replace(" ", "").replace("+", "").replace("-", "")
    if p.startswith("0"):
        return "265" + p[1:]
    return p

def save_file(file, allowed):
    if not file or file.filename == "":
        return ""
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed:
        return ""
    name = uuid.uuid4().hex[:8] + "_" + secure_filename(file.filename)
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], name))
    return name

def get_photos(b):
    try:
        pics = json.loads(b["photos"] or "[]")
    except:
        pics = []
    if pics:
        return ["/uploads/" + p for p in pics]
    if b["photo"]:
        return ["/uploads/" + b["photo"]]
    return CATEGORY_PHOTOS.get(b["category"], CATEGORY_PHOTOS["Other"])

BASE = """
<style>
*{box-sizing:border-box}
body{font-family:Arial,Helvetica,sans-serif;margin:0;background:#EAEDED;color:#0F1111;padding-bottom:70px}
a{text-decoration:none}
.top{background:#131921;color:#fff;padding:10px 12px 8px;position:sticky;top:0;z-index:20}
.toprow{display:flex;align-items:center;gap:8px}
.logo{font-size:22px;font-weight:900;white-space:nowrap}
.logo span{color:#FF9900}
.loc{font-size:11px;line-height:1.2;color:#ccc}
.loc b{color:#fff;font-size:12px}
.search{display:flex;margin-top:10px;background:#fff;border-radius:8px;overflow:hidden;height:42px}
.search select{border:none;background:#F0F2F2;font-size:11px;padding:0 6px;max-width:80px;outline:none}
.search input{flex:1;border:none;outline:none;padding:0 10px;font-size:14px}
.search button{background:#FEBD69;border:none;padding:0 14px;font-size:16px;font-weight:bold}
.subnav{background:#232F3E;color:#fff;display:flex;gap:14px;overflow-x:auto;padding:8px 12px;font-size:12px;white-space:nowrap}
.subnav a{color:#fff}
.install{background:#FFD814;padding:11px 12px;text-align:center;font-weight:bold;font-size:13px;display:none;cursor:pointer;color:#111}
.hero{background:linear-gradient(180deg,#FFD814 0%,#fff 100%);padding:14px;text-align:center}
.hero h2{margin:0;font-size:19px}
.hero p{margin:5px 0 10px;font-size:12px;color:#565959}
.btn-sell{background:#FFD814;border:1px solid #FCD200;padding:10px 18px;border-radius:20px;font-size:13px;font-weight:bold;color:#111;display:inline-block}
.btn-prime{background:#131921;color:#fff;padding:10px 18px;border-radius:20px;font-size:13px;font-weight:bold;display:inline-block;margin-left:6px}
.cats{display:flex;gap:8px;overflow-x:auto;padding:10px 10px 0}
.cats a{background:#fff;border-radius:10px;padding:9px 10px;text-align:center;font-size:11px;color:#111;min-width:64px}
.cats a.active{background:#131921;color:#fff}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:10px}
.card{background:#fff;border-radius:8px;overflow:hidden;display:flex;flex-direction:column}
.card.promoted{border:2px solid #FF9900}
.main-img{width:100%;height:165px;object-fit:cover;display:block;background:#fff}
.thumbs{display:flex;gap:4px;padding:6px 8px 0}
.thumbs img{width:30px;height:30px;object-fit:cover;border-radius:4px;border:1px solid #ddd;cursor:pointer}
.body{padding:8px}
.sponsored{font-size:10px;color:#565959}
.title{font-size:13px;line-height:1.3;margin:3px 0;height:36px;overflow:hidden}
.stars{color:#FFA41C;font-size:12px}
.stars span{color:#007185;font-size:11px}
.price{margin:5px 0}
.price sup{font-size:11px}
.price b{font-size:19px;font-weight:500}
.price small{font-size:11px;color:#565959}
.prime{color:#00A8E1;font-weight:bold;font-size:11px}
.delivery{font-size:11px;color:#565959}
.delivery b{color:#007185}
.stock{color:#007600;font-size:12px}
.btn-buy{background:#FFD814;width:100%;padding:11px;border-radius:20px;font-weight:bold;font-size:13px;margin-top:8px;display:block;text-align:center;color:#111;border:none}
.btn-wa{background:#25D366;color:#fff;width:100%;padding:11px;border-radius:20px;font-weight:bold;font-size:13px;margin-top:6px;display:block;text-align:center}
.btn-edit{display:block;text-align:center;font-size:11px;color:#007185;padding:6px}
.badge-best{background:#E67A00;color:#fff;font-size:10px;padding:2px 6px;border-radius:3px}
.bottom{position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid #ddd;display:flex;justify-content:space-around;padding:8px 0 10px;z-index:30}
.bottom a{text-align:center;font-size:10px;color:#565959}
.bottom a.active{color:#131921;font-weight:bold}
.bottom span{font-size:20px;display:block}
input,select,textarea{width:100%;padding:13px;margin:7px 0;border-radius:8px;border:1px solid #ccc;font-size:15px;background:#fff}
button.submit{width:100%;padding:14px;background:#FFD814;border:1px solid #FCD200;border-radius:20px;font-weight:bold;font-size:15px}
.preview{display:flex;gap:6px;flex-wrap:wrap}
.preview img,.preview video{width:80px;height:80px;object-fit:cover;border-radius:8px}
</style>
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#131921">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Bizworld">
<link rel="apple-touch-icon" href="/icon-192.png">
"""

HOME = BASE + """
<div class="top">
<div class="toprow">
<div class="logo">bizworld<span>.mw</span></div>
<div class="loc">Deliver to<br><b>Malawi</b></div>
<div style="margin-left:auto;font-size:20px">Cart</div>
</div>
<form method="GET" action="/" class="search">
<select name="category"><option value="All">All</option>{% for c in categories %}{% if c != "All" %}<option value="{{c}}">{{cat_short.get(c,c)}}</option>{% endif %}{% endfor %}</select>
<input type="text" name="q" value="{{q}}" placeholder="Search Bizworld...">
<input type="hidden" name="district" value="{{district}}">
<input type="hidden" name="pw" value="{{pw}}">
<button type="submit">Go</button>
</form>
</div>
<div class="subnav"><a href="/">All</a><a href="/?category=Salon & Cosmetics">Beauty</a><a href="/?category=Food">Food</a><a href="/?category=Electronics & Phones">Electronics</a><a href="/add">Sell on Bizworld</a></div>
<div class="install" id="installBar" onclick="doInstall()">Install Bizworld App - Like WhatsApp - Tap Here</div>
<script>
let deferredPrompt;
window.addEventListener("beforeinstallprompt", function(e){ e.preventDefault(); deferredPrompt = e; document.getElementById("installBar").style.display = "block"; });
function doInstall(){ if(deferredPrompt){ deferredPrompt.prompt(); deferredPrompt.userChoice.then(function(){ deferredPrompt = null; }); } else { alert("Android: Tap 3 dots - Install app. iPhone: Share - Add to Home Screen"); } }
if ("serviceWorker" in navigator) { navigator.serviceWorker.register("/sw.js"); }
function changeImg(id, src){ document.getElementById("main-" + id).src = src; }
</script>
<div class="hero">
<h2>Shop in Malawi - Order on WhatsApp</h2>
<p>Best prices - Verified sellers - Fast delivery in Blantyre, Lilongwe, Mzuzu</p>
<a class="btn-sell" href="/add">+ Sell on Bizworld - FREE</a>
<a class="btn-prime" href="https://wa.me/{{owner_whatsapp}}?text=Hi Bizworld, I want to PROMOTE my business." target="_blank">Promote</a>
</div>
<div class="cats">
{% for c in categories %}{% if c != "All" %}<a href="/?district={{district}}&category={{c}}&pw={{pw}}">{{cat_short.get(c,c)}}</a>{% endif %}{% endfor %}
</div>
<div style="padding:6px 10px 0;font-size:11px;color:#565959">Filter: {% for d in districts %}<a href="/?district={{d}}&category={{cat}}&q={{q}}&pw={{pw}}" style="color:#007185">{{d}}</a> - {% endfor %}</div>
<div class="grid">
{% for b in businesses %}
<div class="card">
<img id="main-{{b.id}}" class="main-img" src="{{b.photos_list[0]}}">
{% if b.video %}<video controls src="/uploads/{{b.video}}" style="width:100%;height:120px;background:#000"></video>{% endif %}
<div class="thumbs">{% for t in b.photos_list[1:5] %}<img src="{{t}}" onclick="changeImg({{b.id}}, '{{t}}')">{% endfor %}</div>
<div class="body">
<div class="sponsored">{% if b.promoted %}<span class="badge-best">Best Seller</span>{% else %}Sponsored{% endif %} - {{b.cat_label}}</div>
<div class="title">{{b.name}} - {{b.description}}</div>
<div class="stars">Stars <span>120 ratings</span></div>
<div class="price"><sup>MK</sup> <b>{{b.price}}</b> <small>was MK8000</small></div>
<div class="prime">prime <span style="color:#565959;font-weight:normal">FREE delivery</span></div>
<div class="delivery">Delivery to <b>{{b.town}}, {{b.district}}</b></div>
<div class="stock">In Stock - NEW STOCK</div>
<a class="btn-buy" href="https://wa.me/{{b.whatsapp}}?text=Hi, I want to buy from Bizworld." target="_blank">Buy Now</a>
<a class="btn-wa" href="https://wa.me/{{b.whatsapp}}?text=Hi, I found you on Bizworld." target="_blank">Order on WhatsApp</a>
<a class="btn-edit" href="https://wa.me/{{owner_whatsapp}}?text=Hi Bizworld, update {{b.name}}">Update Stock / Edit</a>
{% if is_admin %}<div style="display:flex;gap:6px"><a class="btn-edit" style="flex:1;color:red" href="/delete/{{b.id}}?pw={{pw}}">Remove</a><a class="btn-edit" style="flex:1" href="/promote/{{b.id}}?pw={{pw}}">Promote</a></div>{% endif %}
</div></div>
{% else %}<p style="grid-column:1/-1;text-align:center">No products found.</p>{% endfor %}
</div>
<div class="bottom">
<a href="/" class="active"><span>Home</span>Home</a>
<a href="/?category=Salon & Cosmetics"><span>Beauty</span>Beauty</a>
<a href="/?category=Food"><span>Food</span>Food</a>
<a href="/add"><span>Sell</span>Sell</a>
<a href="https://wa.me/{{owner_whatsapp}}"><span>Help</span>Help</a>
</div>
"""

ADD = BASE + """
<div style="background:#131921;color:#fff;padding:16px;text-align:center"><h2 style="margin:0">Sell on Bizworld</h2><p style="font-size:12px">Add photos and video - like Amazon seller</p></div>
<div style="padding:16px;background:#fff">
<form method="POST" enctype="multipart/form-data">
<input name="name" placeholder="Product / Business Name" required>
<select name="category" required>{% for c in categories %}<option>{{c}}</option>{% endfor %}</select>
<select name="district" required>{% for d in districts %}<option>{{d}}</option>{% endfor %}</select>
<input name="town" placeholder="Town / Area e.g Chileka" required>
<input name="phone" placeholder="WhatsApp Number e.g 0993066515" required>
<input name="price" placeholder="Price e.g 15000 - without MK">
<textarea name="description" placeholder="Describe your product / business" required></textarea>
<input name="products" placeholder="Products e.g Hair, Nails, Cosmetics">
<label><b>Photos (Select up to 5)</b></label>
<input type="file" name="photos" accept="image/*" multiple onchange="previewPhotos(this)">
<div id="photoPreview" class="preview"></div>
<script>
function previewPhotos(i){var b=document.getElementById("photoPreview");b.innerHTML="";for(var f of i.files){var r=new FileReader();r.onload=function(e){var im=document.createElement("img");im.src=e.target.result;b.appendChild(im);};r.readAsDataURL(f);}}
function previewVideo(i){var b=document.getElementById("videoPreview");b.innerHTML="";if(i.files[0]){var v=document.createElement("video");v.controls=true;v.src=URL.createObjectURL(i.files[0]);b.appendChild(v);}}
</script>
<label><b>Video (1 video)</b></label>
<input type="file" name="video" accept="video/*" onchange="previewVideo(this)">
<div id="videoPreview" class="preview"></div>
<button class="submit" type="submit">List My Product</button>
</form><br><a href="/">Back to Home</a>
</div>
"""

@app.route("/")
def home():
    district = request.args.get("district", "All")
    cat = request.args.get("category", "All")
    q = request.args.get("q", "").strip()
    pw = request.args.get("pw", "")
    is_admin = (pw == ADMIN_PASSWORD)
    con = db()
    sql = "SELECT * FROM businesses WHERE 1=1"
    params = []
    if district != "All":
        sql += " AND district=?"
        params.append(district)
    if cat != "All":
        sql += " AND category=?"
        params.append(cat)
    if q:
        sql += " AND (name LIKE ? OR description LIKE ? OR products LIKE ? OR town LIKE ?)"
        like = "%" + q + "%"
        params += [like, like, like, like]
    sql += " ORDER BY promoted DESC, created_at DESC"
    rows = con.execute(sql, params).fetchall()
    con.close()
    biz = []
    for r in rows:
        d = dict(r)
        d["photos_list"] = get_photos(r)
        d["cat_label"] = CAT_SHORT.get(d["category"], d["category"])
        if not d["price"]:
            d["price"] = "5000"
        biz.append(d)
    return render_template_string(HOME, businesses=biz, count=len(biz), cat_short=CAT_SHORT, districts=["All"] + DISTRICTS, categories=["All"] + CATEGORIES, district=district, cat=cat, q=q, pw=pw, is_admin=is_admin,
