from flask import Flask, request, render_template_string, redirect, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3, os, uuid

app = Flask(__name__)
app.secret_key = "bizworld-secret-change-this-123"
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# >>> PUT YOUR OWN PASSWORD HERE <<<
ADMIN_PASSWORD = "Amigo"

# >>> YOUR WHATSAPP FOR PROMOTION <<<
# Your number 0986765421
OWNER_WHATSAPP = "265986765421"
PROMOTION_PRICE = "MK5,000 for 7 days"

ALLOWED_IMG = {"png","jpg","jpeg","webp","gif"}
ALLOWED_VIDEO = {"mp4","mov","webm","3gp"}

DISTRICTS = ["Blantyre","Lilongwe","Mzuzu","Zomba","Kasungu","Mangochi","Karonga","Salima","Dedza","Other"]
CATEGORIES = ["Salon & Cosmetics","Electronics & Phones","Food","Fashion & Clothes","Phones & Accessories","Grocery & Shops","Services","Other"]

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
body{font-family:Arial,sans-serif;margin:0;padding:16px;background:#f5f5f5;max-width:800px;margin:auto}
h1{font-size:24px} .card{background:#fff;border-radius:14px;padding:16px;margin:14px 0;box-shadow:0 2px 8px #0001}
.card.promoted{border:3px solid #FFD700;background:#FFFEF0}
.btn{background:#25D366;color:#fff;padding:11px 18px;border-radius:10px;text-decoration:none;font-weight:bold;display:inline-block;margin-top:10px}
.btn-black{background:#000;color:#fff;padding:11px 18px;border-radius:10px;text-decoration:none;font-weight:bold;display:inline-block}
.btn-red{background:#ff4444;color:#fff;padding:7px 12px;border-radius:7px;text-decoration:none;font-size:13px}
.btn-gold{background:#FFD700;color:#000;padding:7px 12px;border-radius:7px;text-decoration:none;font-size:13px}
.filter a{display:inline-block;padding:8px 14px;margin:4px;border-radius:20px;background:#eee;color:#000;text-decoration:none;font-size:14px}
.filter a.active{background:#000;color:#fff}
img,video{width:100%;border-radius:10px;margin-top:10px}
input,select,textarea{width:100%;padding:12px;margin:7px 0;border-radius:10px;border:1px solid #ccc;box-sizing:border-box;font-size:15px}
button{width:100%;padding:14px;background:#25D366;color:#fff;border:none;border-radius:10px;font-weight:bold;font-size:16px}
.promo-banner{background:#FFD700;padding:14px;border-radius:12px;text-align:center;margin:12px 0}
.promo-banner a{background:#000;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:bold;display:inline-block;margin-top:6px}
</style>
"""

HOME = BASE_CSS + """
<h1>Bizworld 🇲🇼 - {{count}} Real Businesses</h1>
<p>Find real businesses in Malawi. Chat on WhatsApp directly.</p>

<div class="promo-banner">
<b>⭐ Want your business at the TOP?</b><br>
Promotion: {{promotion_price}}<br>
<a href="https://wa.me/{{owner_whatsapp}}?text=Hi Bizworld, I want to PROMOTE my business. How much is promotion?" target="_blank">⭐ Promote My Business - Chat Owner</a>
</div>

<a class="btn-black" href="/add">+ Add Your Business FREE</a>
{% if is_admin %} <span style="color:green;font-weight:bold"> • ADMIN MODE ON</span> {% endif %}

<form method="GET" action="/" style="margin-top:12px">
<input type="text" name="q" value="{{q}}" placeholder="🔍 Search e.g Meruna, pizza, iPhone, dresses...">
<input type="hidden" name="pw" value="{{pw}}">
<button type="submit" style="background:#000">Search</button>
</form>

<div class="filter"><b>District:</b><br>
{% for d in districts %}<a href="/?district={{d}}&category={{cat}}&q={{q}}&pw={{pw}}" class="{{'active' if d==district else ''}}">{{d}}</a>{% endfor %}</div>
<div class="filter"><b>Category:</b><br>
{% for c in categories %}<a href="/?district={{district}}&category={{c}}&q={{q}}&pw={{pw}}" class="{{'active' if c==cat else ''}}">{{c}}</a>{% endfor %}</div>

{% for b in businesses %}
<div class="card {{'promoted' if b['promoted'] else ''}}">
{% if b['promoted'] %}<div>⭐ <b>PROMOTED / FEATURED BUSINESS</b></div>{% endif %}
<h2>{{b['name']}}</h2>
<p><b>{{b['category']}}</b> • 📍 {{b['town']}}, {{b['district']}}</p>
<p>{{b['description']}}</p><p>{{b['products']}}</p>
{% if b['photo'] %}<img src="/uploads/{{b['photo']}}">{% endif %}
{% if b['video'] %}<video controls src="/uploads/{{b['video']}}"></video>{% endif %}
<br>
<a class="btn" href="https://wa.me/{{b['whatsapp']}}?text=Hi, I found you on Bizworld. I want to order." target="_blank">💬 WhatsApp: {{b['phone']}}</a>
<a href="https://wa.me/{{owner_whatsapp}}?text=Hi Bizworld, I want to PROMOTE my business {{b['name']}}. How much is promotion?" target="_blank" style="display:inline-block;background:#FFD700;color:#000;padding:11px 16px;border-radius:10px;text-decoration:none;font-weight:bold;margin-top:10px;margin-left:5px">⭐ Promote Me</a>
{% if is_admin %}<br><br>
<a class="btn-red" href="/delete/{{b['id']}}?pw={{pw}}">🗑 Remove</a>
<a class="btn-gold" href="/promote/{{b['id']}}?pw={{pw}}">{{'Unpromote' if b['promoted'] else '⭐ Promote'}}</a>
{% endif %}
</div>
{% else %}<p>No businesses found. Try All.</p>{% endfor %}
<hr><p style="text-align:center;color:#888">Bizworld Malawi • Made for Malawian Businesses</p>
"""

ADD = BASE_CSS + """
<h1>+ Add Your Business FREE</h1>
<p>Fill this form. Add photo / video from your phone. It will appear immediately.</p>
<form method="POST" enctype="multipart/form-data">
<input name="name" placeholder="Business Name" required>
<select name="category" required>{% for c in categories %}<option>{{c}}</option>{% endfor %}</select>
<select name="district" required>{% for d in districts %}<option>{{d}}</option>{% endfor %}</select>
<input name="town" placeholder="Town / Area e.g Chileka" required>
<input name="phone" placeholder="WhatsApp Number e.g 0993066515" required>
<textarea name="description" placeholder="What do you sell?" required></textarea>
<input name="products" placeholder="Products e.g Hair, Nails, Cosmetics">
<label><b>📸 Business Photo (from phone)</b></label><input type="file" name="photo" accept="image/*">
<label><b>🎥 Business Video (from phone, max 50MB)</b></label><input type="file" name="video" accept="video/*">
<button type="submit">ADD MY BUSINESS ✅</button>
</form><br><a href="/">← Back</a>
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
    return r(HOME, businesses=rows, count=len(rows), districts=["All"]+DISTRICTS, categories=["All"]+CATEGORIES, district=district, cat=cat, q=q, pw=pw, is_admin=is_admin, owner_whatsapp=OWNER_WHATSAPP, promotion_price=PROMOTION_PRICE)

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

if __name__ == "__main__":
    app.run(debug=True)
