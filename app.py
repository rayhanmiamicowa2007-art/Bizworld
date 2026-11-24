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
EMOJI = {"Food": "FOOD", "Fashion": "FASHION", "Beauty": "BEAUTY", "Phones": "PHONE", "Services": "SERVICE"}

BASE = """
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#0f172a">
<style>
body{margin:0;background:#f6f7fb;font-family:Arial}
header{background:#0f172a;color:white;padding:28px 16px;text-align:center}
header a{background:#22c55e;color:white;padding:11px 18px;border-radius:999px;text-decoration:none;font-weight:700;display:inline-block;margin:4px}
header a.gold{background:#f59e0b;color:#111}
header a.install{background:white;color:#0f172a;border:2px solid #22c55e}
.grid{max-width:900px;margin:0 auto;padding:12px;display:grid;grid-template-columns:1fr 1fr;gap:14px}
.card{background:white;border-radius:16px;overflow:hidden;box-shadow:0 4px 18px rgba(0,0,0,.06)}
.card-img{height:220px;background:#e0e7ff;display:flex;align-items:center;justify-content:center;overflow:hidden}
.card-img img{width:100%;height:100%;object-fit:cover}
.thumbs{display:flex;gap:6px;padding:8px}
.thumbs img{width:60px;height:60px;object-fit:cover;border-radius:8px;cursor:pointer}
.card-body{padding:16px}
.wa{display:block;text-align:center;background:#22c55e;color:white;padding:12px;border-radius:10px;text-decoration:none;font-weight:800;margin-top:12px}
.update{display:block;text-align:center;background:white;color:#111;border:1px solid #ddd;padding:10px;border-radius:10px;text-decoration:none;margin-top:8px}
.form{max-width:600px;margin:20px auto;background:white;padding:20px;border-radius:16px}
.form input,.form select,.form textarea{width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:10px}
.form button{width:100%;padding:14px;background:#0f172a;color:white;border:none;border-radius:10px;font-weight:800}
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
 main.src=el.getAttribute("data-src");
}
</script>
"""

@app.route("/manifest.json")
def manifest():
    return {"name": "Bizworld Malawi", "short_name": "Bizworld", "display": "standalone", "start_url": "/", "background_color": "#0f172a", "theme_color": "#0f172a", "icons": [{"src": "https://cdn-icons-png.flaticon.com/512/744/744465.png", "sizes": "512x512", "type": "image/png"}]}

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
        filt = [b for b in filt if q in b["name"].lower() or q in b["desc"].lower()]
    cards = ""
    for b in filt:
        real_idx = BUSINESSES.index(b)
        wa = quote("Hi " + b["name"] + "! I found you on Bizworld.")
        feat = "FEATURED " if b.get("featured") else ""
        is_new = False
        if b.get("updated", 0) > 0:
            if time.time() - b.get("updated", 0) < 7*24*3600:
                is_new = True
        new = "NEW STOCK! " if is_new else ""
        imgs = b.get("images", [])
        if imgs:
            top = "<div class='card-img'><img src='" + imgs[0] + "'></div>"
            if len(imgs) > 1:
                th = "<div class='thumbs'>"
                for im in imgs:
                    th += "<img src='" + im + "' data-src='" + im + "' onclick='swapThumb(this)'>"
                th += "</div>"
                top = top + th
        else:
            top = "<div class='card-img'>" + EMOJI.get(b["category"], "SHOP") + "</div>"
        delbtn = ""
        if admin:
            delbtn = "<a href='/delete/" + str(real_idx) + "'>Delete</a> "
        one = "<div class='card'>"
        one += delbtn + top
        one += "<div class='card-body'><b>" + feat + new + b["name"] + "</b>"
        one += "<p>" + b["desc"] + "</p>"
        one += "<p>" + b["location"] + " - " + b["price"] + "</p>"
        one += "<a class='wa' href='https://wa.me/" + b["phone"] + "?text=" + wa + "'>Order on WhatsApp</a>"
        one += "<a class='update' href='/edit/" + str(real_idx) + "'>Update Stock / Edit</a>"
        one += "</div></div>"
        cards += one
    page = BASE
    page += "<header><h1>Bizworld</h1><p>Find businesses in Malawi. Order on WhatsApp.</p>"
    page += "<a href='/add'>Add Your Business - FREE</a>"
    page += "<a class='gold' href='/featured'>Promote My Business</a><br>"
    page += "<a class='install' href='#' onclick='installApp();return false;'>Install Bizworld App</a></header>"
    page += "<div class='grid'>" + cards + "</div>"
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
    page += "<header><h1>Add Your Business</h1></header>"
    page += "<form class='form' method='post' enctype='multipart/form-data'>"
    page += "<input name='name' placeholder='Business Name' required>"
    page += "<select name='city'><option>Lilongwe</option><option>Blantyre</option><option>Mzuzu</option><option>Zomba</option></select>"
    page += "<select name='category'><option>Food</option><option>Fashion</option><option>Beauty</option><option>Phones</option><option>Services</option></select>"
    page += "<textarea name='desc' placeholder='What do you sell?' required></textarea>"
    page += "<input name='price' placeholder='Price' required>"
    page += "<input name='phone' placeholder='WhatsApp 265...' required>"
    page += "<input name='location' placeholder='Location' required>"
    page += "<label>Photos up to 4</label><input type='file' name='photos' accept='image/*' multiple>"
    page += "<input name='video' placeholder='TikTok link'>"
    page += "<button>Publish</button></form>"
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
    page += "<header><h1>Update Stock</h1><p>" + b["name"] + "</p></header>"
    page += "<form class='form' method='post' enctype='multipart/form-data'>"
    page += "<input name='verify_phone' placeholder='Your WhatsApp number' required>"
    page += "<input name='pin' type='password' placeholder='Admin PIN optional'>"
    page += "<input name='name' value='" + b["name"] + "' required>"
    page += "<textarea name='desc' required>" + b["desc"] + "</textarea>"
    page += "<input name='price' value='" + b["price"] + "' required>"
    page += "<input name='location' value='" + b["location"] + "' required>"
    page += "<input type='file' name='photos' accept='image/*' multiple>"
    page += "<button>Update My Stock</button></form>"
    return render_template_string(page)

@app.route("/featured")
def featured():
    wa = quote("Hi Bizworld! I want FEATURED")
    page = BASE
    page += "<header><h1>Promote Your Business</h1></header>"
    page += "<div class='form'><h3>Featured 1 Week K5,000</h3><h3>Featured 1 Month K15,000</h3>"
    page += "<a class='wa' href='https://wa.me/" + OWNER_PHONE + "?text=" + wa + "'>Pay via WhatsApp</a></div>"
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
