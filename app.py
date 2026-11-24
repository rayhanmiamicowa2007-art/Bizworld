from flask import Flask, request, redirect, url_for, render_template_string
from urllib.parse import quote
import json, os, base64, time

app = Flask(__name__)
DATA_FILE = "businesses.json"
ADMIN_PIN = "1995"
OWNER_PHONE = "265986765421"

DEFAULT = [
 {"name": "Lilongwe Fresh Foods", "category": "Food", "city": "Lilongwe", "desc": "Fresh vegetables and groceries.", "price": "From K2,000", "phone": "265880123456", "location": "Area 47, Lilongwe", "featured": True, "images": [], "video": "", "updated": 0},
 {"name": "Glow Beauty Salon", "category": "Beauty", "city": "Lilongwe", "desc": "Braiding, nails, makeup and wigs.", "price": "From K5,000", "phone": "265991234567", "location": "Old Town, Lilongwe", "featured": True, "images": [], "video": "", "updated": 0},
 {"name": "TechFix Malawi", "category": "Phones", "city": "Lilongwe", "desc": "Phone repair in 30 mins.", "price": "From K10,000", "phone": "265882345678", "location": "City Centre, Lilongwe", "featured": False, "images": [], "video": "", "updated": 0},
]

def load():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                d = json.load(f)
                for b in d:
                    b.setdefault("city", "Lilongwe")
                    b.setdefault("video", "")
                    b.setdefault("updated", 0)
                    b.setdefault("images", [])
                return d
        except:
            return list(DEFAULT)
    return list(DEFAULT)

def save(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f)

BUSINESSES = load()
CATEGORIES = ["All", "Food", "Fashion", "Beauty", "Phones", "Services"]
CITIES = ["All", "Lilongwe", "Blantyre", "Mzuzu", "Zomba", "Mzimba"]
EMOJI = {"Food": "🍲", "Fashion": "👗", "Beauty": "💅", "Phones": "📱", "Services": "🧹"}

BASE = """
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#7c3aed">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{box-sizing:border-box}
body{margin:0;background:#f8f7ff;font-family:Arial;color:#111;padding-bottom:80px}
header{background:linear-gradient(135deg,#7c3aed,#db2777);color:white;padding:26px 16px 32px;text-align:center;border-radius:0 0 28px 28px}
header h1{margin:0;font-size:34px;letter-spacing:-1px}
header p{opacity:.9;margin:8px 0 16px;font-size:14px}
.topbtn{display:inline-block;background:white;color:#7c3aed;padding:11px 18px;border-radius:999px;text-decoration:none;font-weight:800;font-size:14px;margin:3px}
.topbtn.gold{background:#facc15;color:#111}
.topbtn.install{background:transparent;color:white;border:2px solid white}
.searchbar{max-width:900px;margin:-14px auto 0;background:white;padding:10px;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,.12);display:flex;gap:8px;margin-left:12px;margin-right:12px}
.searchbar input{flex:1;border:none;outline:none;padding:10px;font-size:15px}
.searchbar button{background:#7c3aed;color:white;border:none;padding:10px 16px;border-radius:12px;font-weight:800}
.pills{max-width:900px;margin:14px auto 0;padding:0 12px;display:flex;gap:8px;overflow-x:auto;white-space:nowrap}
.pills a{background:white;padding:9px 16px;border-radius:999px;text-decoration:none;color:#333;font-size:13px;font-weight:700;box-shadow:0 2px 8px rgba(0,0,0,.05)}
.pills a.on{background:#111;color:white}
.pills a.cityon{background:#16a34a;color:white}
.section{max-width:900px;margin:18px auto 0;padding:0 12px;display:flex;justify-content:space-between;align-items:center}
.section h2{margin:0;font-size:18px}
.section span{color:#7c3aed;font-size:13px;font-weight:800}
.grid{max-width:900px;margin:10px auto;padding:0 12px;display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:600px){.grid{grid-template-columns:1fr 1fr;gap:10px}}
.card{background:white;border-radius:20px;overflow:hidden;box-shadow:0 6px 20px rgba(0,0,0,.07);position:relative}
.card-img{height:160px;background:linear-gradient(135deg,#ddd6fe,#fbcfe8);display:flex;align-items:center;justify-content:center;font-size:64px;overflow:hidden;position:relative}
.card-img img{width:100%;height:100%;object-fit:cover}
.card-img .tag{position:absolute;top:8px;left:8px;background:#facc15;color:#111;font-size:11px;font-weight:800;padding:5px 9px;border-radius:999px}
.card-img .new{position:absolute;top:8px;right:8px;background:#22c55e;color:white;font-size:11px;font-weight:800;padding:5px 9px;border-radius:999px}
.thumbs{display:flex;gap:5px;padding:8px 8px 0}
.thumbs img{width:42px;height:42px;object-fit:cover;border-radius:10px;border:2px solid #eee}
.card-body{padding:12px}
.card-body .cat{font-size:11px;color:#7c3aed;font-weight:800;text-transform:uppercase}
.card-body h3{margin:4px 0;font-size:15px;line-height:1.2}
.card-body p{margin:4px 0;color:#666;font-size:12px;line-height:1.4}
.price{color:#16a34a;font-weight:900;font-size:15px}
.loc{color:#888;font-size:11px}
.wa{display:flex;align-items:center;justify-content:center;gap:6px;background:#22c55e;color:white;padding:11px;border-radius:12px;text-decoration:none;font-weight:800;font-size:13px;margin-top:10px}
.update{display:block;text-align:center;color:#555;font-size:12px;margin-top:8px;text-decoration:none}
.bottom{position:fixed;bottom:0;left:0;right:0;background:white;display:flex;justify-content:space-around;padding:12px 0 16px;border-top:1px solid #eee;z-index:99}
.bottom a{text-decoration:none;color:#888;font-size:12px;text-align:center;font-weight:700}
.bottom a.on{color:#7c3aed}
.form{max-width:600px;margin:20px auto;background:white;padding:20px;border-radius:20px}
.form input,.form select,.form textarea{width:100%;padding:13px;margin:8px 0;border:1px solid #ddd;border-radius:12px;font-size:15px}
.form button{width:100%;padding:15px;background:#7c3aed;color:white;border:none;border-radius:12px;font-weight:800;font-size:16px}
.plan{background:white;border-radius:20px;padding:20px;margin:12px 0;border:2px solid #eee}
.plan.hot{border-color:#f59e0b;background:#fffbeb}
</style>
<script>
if("serviceWorker" in navigator){navigator.serviceWorker.register("/sw.js");}
let deferredPrompt=null;
window.addEventListener("beforeinstallprompt",function(e){e.preventDefault();deferredPrompt=e;});
function installApp(){
 if(deferredPrompt){deferredPrompt.prompt();}
 else{alert("Tap 3 dots in Chrome then Install app. On iPhone Share then Add to Home Screen");}
}
function swapThumb(el){
 var card=el.closest(".card");
 var main=card.querySelector(".card-img img");
 if(main){main.src=el.getAttribute("data-src");}
}
</script>
"""

@app.route("/manifest.json")
def manifest():
    return {"name": "Bizworld Malawi", "short_name": "Bizworld", "display": "standalone", "start_url": "/", "background_color": "#7c3aed", "theme_color": "#7c3aed", "icons": [{"src": "https://cdn-icons-png.flaticon.com/512/744/744465.png", "sizes": "512x512", "type": "image/png"}]}

@app.route("/sw.js")
def sw():
    js = "self.addEventListener('install',function(e){self.skipWaiting();});"
    return js, 200, {"Content-Type": "application/javascript"}

@app.route("/")
def home():
    q = request.args.get("q", "").lower().strip()
    cat = request.args.get("cat", "All")
    city = request.args.get("city", "All")
    admin = request.args.get("admin") == "1"
    filt = BUSINESSES
    if cat != "All":
        filt = [b for b in filt if b["category"] == cat]
    if city != "All":
        filt = [b for b in filt if b.get("city", "Lilongwe") == city]
    if q:
        filt = [b for b in filt if q in b["name"].lower() or q in b["desc"].lower() or q in b["location"].lower()]
    # Featured first, then NEW first
    filt = sorted(filt, key=lambda b: (not b.get("featured", False)))
    cards = ""
    for b in filt:
        real_idx = BUSINESSES.index(b)
        wa = quote("Hi " + b["name"] + "! I found you on Bizworld.")
        tag = ""
        if b.get("featured"):
            tag = "<span class='tag'>⭐ FEATURED</span>"
        is_new = False
        if b.get("updated", 0) > 0:
            if time.time() - b.get("updated", 0) < 7*24*3600:
                is_new = True
        newb = ""
        if is_new:
            newb = "<span class='new'>🆕 NEW</span>"
        imgs = b.get("images", [])
        if imgs:
            top = "<div class='card-img'>" + tag + newb + "<img src='" + imgs[0] + "'></div>"
            if len(imgs) > 1:
                th = "<div class='thumbs'>"
                for im in imgs:
                    th += "<img src='" + im + "' data-src='" + im + "' onclick='swapThumb(this)'>"
                th += "</div>"
                top = top + th
        else:
            emoji = EMOJI.get(b["category"], "🏪")
            top = "<div class='card-img'>" + tag + newb + "<span>" + emoji + "</span></div>"
        delbtn = ""
        if admin:
            delbtn = "<a href='/delete/" + str(real_idx) + "'>Delete</a> "
        one = "<div class='card'>"
        one += delbtn + top
        one += "<div class='card-body'>"
        one += "<div class='cat'>" + b["category"] + " • " + b.get("city", "Lilongwe") + "</div>"
        one += "<h3>" + b["name"] + "</h3>"
        one += "<p>" + b["desc"] + "</p>"
        one += "<p class='loc'>📍 " + b["location"] + "</p>"
        one += "<div class='price'>" + b["price"] + "</div>"
        one += "<a class='wa' href='https://wa.me/" + b["phone"] + "?text=" + wa + "'>💬 Order on WhatsApp</a>"
        one += "<a class='update' href='/edit/" + str(real_idx) + "'>🔄 Update Stock</a>"
        one += "</div></div>"
        cards += one
    if not cards:
        cards = "<p style='text-align:center;grid-column:1/-1;'>No businesses found. Try another city.</p>"
    city_pills = ""
    for c in CITIES:
        cls = "cityon" if c == city else ""
        city_pills += "<a class='" + cls + "' href='/?city=" + c + "&cat=" + cat + "'>📍 " + c + "</a>"
    cat_pills = ""
    for c in CATEGORIES:
        cls = "on" if c == cat else ""
        cat_pills += "<a class='" + cls + "' href='/?cat=" + c + "&city=" + city + "'>" + c + "</a>"
    qval = request.args.get("q", "")
    page = BASE
    page += "<header><h1>🌍 Bizworld</h1>"
    page += "<p>Find the best businesses in Malawi 🇲🇼 Order on WhatsApp</p>"
    page += "<a class='topbtn' href='/add'>+ Add Business FREE</a>"
    page += "<a class='topbtn gold' href='/featured'>⭐ Promote</a><br>"
    page += "<a class='topbtn install' href='#' onclick='installApp();return false;'>📱 Install App</a></header>"
    page += "<form class='searchbar' method='get' action='/'>"
    page += "<input name='q' placeholder='🔍 Search perfumes, food, salon...' value='" + qval + "'>"
    page += "<button>Search</button></form>"
    page += "<div class='pills'>" + city_pills + "</div>"
    page += "<div class='pills'>" + cat_pills + "</div>"
    page += "<div class='section'><h2>🔥 Trending Near You</h2><span>See All →</span></div>"
    page += "<div class='grid'>" + cards + "</div>"
    page += "<div class='bottom'>"
    page += "<a class='on' href='/'>🏠<br>Home</a>"
    page += "<a href='/?cat=Beauty&city=" + city + "'>💅<br>Beauty</a>"
    page += "<a href='/add'>➕<br>Sell</a>"
    page += "<a href='/featured'>⭐<br>Promote</a>"
    page += "</div>"
    return render_template_string(page)

def process_images(req):
    out = []
    for f in req.files.getlist("photos")[:4]:
        if f and f.filename != "":
            data = f.read()
            if len(data) < 1500000:
                b64 = base64.b64encode(data).decode("utf-8")
                out.append("data:" + str(f.mimetype) + ";base64," + b64)
    return out

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        nb = {}
        nb["name"] = request.form.get("name")
        nb["category"] = request.form.get("category")
        nb["city"] = request.form.get("city")
        nb["desc"] = request.form.get("desc")
        nb["price"] = request.form.get("price")
        nb["phone"] = request.form.get("phone").replace("+", "").replace(" ", "")
        nb["location"] = request.form.get("location")
        nb["featured"] = False
        nb["images"] = process_images(request)
        nb["video"] = request.form.get("video", "").strip()
        nb["updated"] = time.time()
        BUSINESSES.insert(0, nb)
        save(BUSINESSES)
        return redirect(url_for("home"))
    page = BASE
    page += "<header><h1>+ Add Business</h1><p>Join Bizworld - Get customers on WhatsApp</p></header>"
    page += "<form class='form' method='post' enctype='multipart/form-data'>"
    page += "<input name='name' placeholder='Business Name' required>"
    page += "<select name='city'><option>Lilongwe</option><option>Blantyre</option><option>Mzuzu</option><option>Zomba</option></select>"
    page += "<select name='category'><option>Food</option><option>Fashion</option><option>Beauty</option><option>Phones</option><option>Services</option></select>"
    page += "<textarea name='desc' placeholder='What do you sell?' required></textarea>"
    page += "<input name='price' placeholder='Price e.g. From K15,000' required>"
    page += "<input name='phone' placeholder='WhatsApp 265...' required>"
    page += "<input name='location' placeholder='Location' required>"
    page += "<label>📸 Photos up to 4</label><input type='file' name='photos' accept='image/*' multiple>"
    page += "<input name='video' placeholder='TikTok / YouTube link'>"
    page += "<button>Publish My Business →</button></form>"
    return render_template_string(page)

@app.route("/edit/<int:idx>", methods=["GET", "POST"])
def edit(idx):
    if idx >= len(BUSINESSES):
        return redirect("/")
    b = BUSINESSES[idx]
    if request.method == "POST":
        entered = request.form.get("verify_phone", "").replace("+", "").replace(" ", "")
        if entered != b["phone"] and request.form.get("pin", "") != ADMIN_PIN:
            return "Wrong number. Only owner can edit."
        b["name"] = request.form.get("name")
        b["desc"] = request.form.get("desc")
        b["price"] = request.form.get("price")
        b["location"] = request.form.get("location")
        ni = process_images(request)
        if ni:
            b["images"] = ni
        b["updated"] = time.time()
        save(BUSINESSES)
        return redirect(url_for("home"))
    page = BASE
    page += "<header><h1>🔄 Update Stock</h1><p>" + b["name"] + "</p></header>"
    page += "<form class='form' method='post' enctype='multipart/form-data'>"
    page += "<input name='verify_phone' placeholder='Your WhatsApp number' required>"
    page += "<input name='pin' type='password' placeholder='Admin PIN optional'>"
    page += "<input name='name' value='" + b["name"] + "' required>"
    page += "<textarea name='desc' required>" + b["desc"] + "</textarea>"
    page += "<input name='price' value='" + b["price"] + "' required>"
    page += "<input name='location' value='" + b["location"] + "' required>"
    page += "<label>📸 New Photos</label><input type='file' name='photos' accept='image/*' multiple>"
    page += "<button>✅ Update My Stock - Show as NEW!</button></form>"
    return render_template_string(page)

@app.route("/featured")
def featured():
    wa = quote("Hi Bizworld! I want FEATURED")
    page = BASE
    page += "<header><h1>⭐ Promote Your Business</h1><p>Be at the top. Get more customers.</p></header>"
    page += "<div class='form'><h3>⭐ Featured 1 Week - K5,000</h3><p>Yellow badge + Top of homepage</p>"
    page += "<h3>🔥 Featured 1 Month - K15,000</h3><p>Best value - Full month at top</p>"
    page += "<h3>👑 Top Spot 1 Month - K25,000</h3><p>Very first card</p>"
    page += "<a class='wa' href='https://wa.me/" + OWNER_PHONE + "?text=" + wa + "'>Pay via WhatsApp →</a></div>"
    return render_template_string(page)

@app.route("/delete/<int:idx>", methods=["GET", "POST"])
def delete(idx):
    if request.method == "POST":
        if request.form.get("pin") == ADMIN_PIN and 0 <= idx < len(BUSINESSES):
            del BUSINESSES[idx]
            save(BUSINESSES)
            return "Deleted. <a href='/?admin=1'>Back</a>"
        return "Wrong PIN"
    page = BASE
    page += "<form class='form' method='post'>"
    page += "<p>Delete " + BUSINESSES[idx]["name"] + "?</p>"
    page += "<input name='pin' type='password' placeholder='Admin PIN' required>"
    page += "<button>Yes Delete</button></form>"
    return render_template_string(page)

if __name__ == "__main__":
    app.run(debug=True)
