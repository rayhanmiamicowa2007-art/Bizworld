from flask import Flask, request, render_template_string, redirect, send_from_directory, Response
from werkzeug.utils import secure_filename
import sqlite3, os, uuid, json, struct, zlib
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs("uploads", exist_ok=True)
ADMIN_PASSWORD = "1995"
OWNER = "265986765421"
DISTRICTS = ["Blantyre","Lilongwe","Mzuzu","Zomba","Mzimba","Kasungu","Mangochi","Karonga","Salima","Dedza","Other"]
CATEGORIES = ["Salon & Cosmetics","Electronics & Phones","Food","Fashion & Clothes","Phones & Accessories","Grocery & Shops","Services","Other"]
SHORT = {"Salon & Cosmetics":"Beauty","Electronics & Phones":"Electronics","Food":"Food","Fashion & Clothes":"Fashion","Phones & Accessories":"Phones","Grocery & Shops":"Grocery","Services":"Services","Other":"Other"}
EMOJI = {"Salon & Cosmetics":"💇‍♀️","Electronics & Phones":"💻","Food":"🍔","Fashion & Clothes":"👗","Phones & Accessories":"📱","Grocery & Shops":"🛒","Services":"🔧","Other":"🛍️"}
PHOTOS = {"Salon & Cosmetics":"https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800&q=80","Electronics & Phones":"https://images.unsplash.com/photo-1498049794561-7780e7231661?w=800&q=80","Food":"https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80","Fashion & Clothes":"https://images.unsplash.com/photo-1445205170230-053b83016050?w=800&q=80","Phones & Accessories":"https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&q=80","Grocery & Shops":"https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=800&q=80","Services":"https://images.unsplash.com/photo-1521791136064-7986c2920216?w=800&q=80","Other":"https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&q=80"}
def db():
    c = sqlite3.connect("bizworld.db")
    c.row_factory = sqlite3.Row
    return c
def init():
    c = db()
    c.execute("CREATE TABLE IF NOT EXISTS businesses (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, district TEXT, town TEXT, phone TEXT, whatsapp TEXT, description TEXT, products TEXT, photo TEXT, video TEXT, price TEXT, photos TEXT, promoted INTEGER DEFAULT 0)")
    c.commit()
    n = c.execute("SELECT COUNT(*) FROM businesses").fetchone()[0]
    if n == 0:
        seed = [("Meruna salon and cosmetics","Salon & Cosmetics","Blantyre","Chileka","0993066515","265993066515","We sell cosmetics and we are doing salon","Hair Nails","15000",1),("Wow Skin Care Malawi","Salon & Cosmetics","Blantyre","Mandala","0887616804","265887616804","Original skincare and hair care. Nationwide delivery.","Skincare","25000",0),("Kips Restaurant","Food","Blantyre","Blantyre City","0883999999","265883999999","Restaurant and ice cream. FREE delivery.","Pizza Burgers","12000",0),("Fatha Hi-Tech","Electronics & Phones","Lilongwe","City Centre","0999621027","265999621027","Laptops, printers, monitors.","Laptops","850000",0),("Cherries Collection","Fashion & Clothes","Mzuzu","Mzuzu City","0993185015","265993185015","Womens dresses MK30k-35k.","Dresses","32000",0)]
        for s in seed:
            c.execute("INSERT INTO businesses (name,category,district,town,phone,whatsapp,description,products,price,promoted) VALUES (?,?,?,?,?,?,?,?,?,?)", s)
        c.commit()
    c.close()
init()
def towa(p):
    p = p.strip().replace(" ","").replace("+","").replace("-","")
    return "265" + p[1:] if p.startswith("0") else p
def save(f, allowed):
    if not f or f.filename == "":
        return ""
    ext = f.filename.rsplit(".",1)[-1].lower()
    if ext not in allowed:
        return ""
    n = uuid.uuid4().hex[:8] + "_" + secure_filename(f.filename)
    f.save(os.path.join("uploads", n))
    return n
def getpics(b):
    try:
        pics = json.loads(b["photos"] or "[]")
    except:
        pics = []
    if pics:
        return ["/uploads/" + p for p in pics]
    if b["photo"]:
        return ["/uploads/" + b["photo"]]
    return [PHOTOS.get(b["category"], PHOTOS["Other"])]
def make_png(size):
    def chunk(t, data):
        c = struct.pack(">I", len(data)) + t + data
        c += struct.pack(">I", zlib.crc32(t + data) & 0xffffffff)
        return c
    raw = b""
    for y in range(size):
        raw += b"\x00"
        for x in range(size):
            if size//4 < x < size*3//4 and size//4 < y < size*3//4:
                raw += bytes([255, 184, 0, 255])
            else:
                raw += bytes([19, 25, 33, 255])
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
CSS = "<style>*{box-sizing:border-box}body{font-family:Arial;margin:0;background:#F0F2F5;padding-bottom:76px}a{text-decoration:none}.top{background:#131921;color:#fff;padding:12px 12px 14px;position:sticky;top:0;z-index:20;border-radius:0 0 18px 18px}.toprow{display:flex;justify-content:space-between;align-items:center}.logo{font-size:26px;font-weight:900;letter-spacing:-1px}.logo span{color:#FF9900}.badge{background:#FF9900;color:#111;font-size:10px;padding:3px 8px;border-radius:20px;font-weight:800}.loc{font-size:11px;color:#ccc;margin-top:2px}.search{display:flex;margin-top:12px;background:#fff;border-radius:30px;overflow:hidden;height:48px;box-shadow:0 4px 12px #0003}.search input{flex:1;border:none;outline:none;padding:0 16px;font-size:15px}.search button{background:#FF9900;border:none;padding:0 20px;font-size:18px}.install{background:#FFD814;padding:12px;text-align:center;font-weight:800;display:none;cursor:pointer;color:#111;font-size:14px}.hero{margin:12px;border-radius:20px;overflow:hidden;background:linear-gradient(135deg,#131921,#FF9900);color:#fff;padding:20px;position:relative}.hero h1{margin:0;font-size:27px;line-height:1.1}.hero p{color:#FFE9B0;margin:10px 0 16px}.btn-sell{background:#FFD814;padding:12px 22px;border-radius:25px;font-weight:800;color:#111;display:inline-block}.btn-prime{background:#fff;padding:12px 22px;border-radius:25px;font-weight:800;color:#111;display:inline-block;margin-left:6px}.trust{display:flex;gap:8px;margin:12px}.trust div{flex:1;background:#fff;border-radius:14px;padding:10px;text-align:center;font-size:11px;font-weight:bold;box-shadow:0 2px 8px #0001}.cats{display:flex;gap:10px;overflow-x:auto;padding:4px 12px 12px;scrollbar-width:none}.cats a{background:#fff;border-radius:16px;padding:12px 10px;text-align:center;font-size:12px;color:#111;min-width:76px;box-shadow:0 2px 8px #0001}.cats a b{display:block;font-size:26px}.sec{padding:6px 14px;font-weight:900;font-size:18px;display:flex;justify-content:space-between;align-items:center}.sec small{color:#FF9900;font-size:12px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:0 12px}.card{background:#fff;border-radius:18px;overflow:hidden;box-shadow:0 4px 14px #0001;position:relative}.disc{position:absolute;top:10px;left:10px;background:#E5002B;color:#fff;font-size:11px;font-weight:800;padding:4px 8px;border-radius:20px;z-index:2}.main-img{width:100%;height:180px;object-fit:cover}.thumbs{display:flex;gap:4px;padding:6px}.thumbs img{width:32px;height:32px;object-fit:cover;border-radius:8px;border:2px solid #eee}.body{padding:10px 12px 12px}.price{margin:4px 0}.price b{font-size:20px}.price s{color:#999;font-size:12px}.prime{color:#00A8E1;font-weight:800;font-size:11px}.stock{color:#007600;font-size:12px;font-weight:600}.btn-buy{background:linear-gradient(90deg,#FFD814,#FF9900);width:100%;padding:12px;border-radius:25px;font-weight:800;display:block;text-align:center;color:#111;margin-top:8px;box-shadow:0 3px 8px #FF990066}.btn-wa{background:#25D366;color:#fff;width:100%;padding:12px;border-radius:25px;font-weight:800;margin-top:6px;display:block;text-align:center}.bottom{position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid #eee;display:flex;justify-content:space-around;padding:12px 0 16px;z-index:30;border-radius:18px 18px 0 0}.bottom a{text-align:center;font-size:11px;color:#888}.bottom a.active{color:#131921;font-weight:800}.bottom a b{display:block;font-size:20px}input,select,textarea{width:100%;padding:14px;margin:7px 0;border-radius:12px;border:1px solid #ddd}.submit{width:100%;padding:15px;background:linear-gradient(90deg,#FFD814,#FF9900);border:none;border-radius:25px;font-weight:800}</style><link rel=manifest href=/manifest.json><meta name=theme-color content=#131921><meta name=mobile-web-app-capable content=yes><meta name=apple-mobile-web-app-capable content=yes><meta name=apple-mobile-web-app-title content=Bizworld><link rel=apple-touch-icon href=/icon-192.png>"
HOME = CSS + """
<div class=top><div class=toprow><div class=logo>bizworld<span>.mw</span></div><div class=badge>★ MALAWI #1</div></div><div class=loc>📍 Deliver to Malawi - Fast Delivery - Cash on Delivery</div><form method=GET action=/ class=search><input name=q value="{{q}}" placeholder="Search products, shops..."><input type=hidden name=district value="{{district}}"><input type=hidden name=pw value="{{pw}}"><button>🔍</button></form></div>
<div class=install id=installBar onclick=doInstall()>📲 INSTALL BIZWORLD APP - Tap Here - Like WhatsApp</div>
<script>let dp;window.addEventListener("beforeinstallprompt",function(e){e.preventDefault();dp=e;document.getElementById("installBar").style.display="block";});function doInstall(){if(dp){dp.prompt();}else{alert("Tap 3 dots - Add to Home screen");}}if("serviceWorker" in navigator){navigator.serviceWorker.register("/sw.js");}function ch(id,s){document.getElementById("m"+id).src=s;}</script>
<div class=hero><h1>Shop in Malawi<br>Like Amazon 🇲🇼</h1><p>Best Prices • Verified Sellers • Order on WhatsApp</p><a class=btn-sell href=/add>+ Sell FREE</a> <a class=btn-prime href="https://wa.me/{{owner}}">Promote 🚀</a></div>
<div class=trust><div>🚚<br>Fast Delivery</div><div>✅<br>Verified Sellers</div><div>💵<br>Cash on Delivery</div><div>↩️<br>Easy Returns</div></div>
<div class=sec>Shop by Category <small>View all →</small></div>
<div class=cats>{% for c in categories %}{% if c != "All" %}<a href="/?district={{district}}&category={{c}}&pw={{pw}}"><b>{{emoji.get(c,"🛍️")}}</b>{{cat_short.get(c,c)}}</a>{% endif %}{% endfor %}</div>
<div class=sec>🔥 Featured Today <small>Best Sellers</small></div>
<div style="padding:0 14px 10px;font-size:12px;color:#666">Filter: {% for d in districts %}<a href="/?district={{d}}&category={{cat}}&pw={{pw}}" style="color:#007185">{{d}}</a> • {% endfor %}</div>
<div class=grid>{% for b in businesses %}<div class=card><div class=disc>-20% OFF</div><img id="m{{b.id}}" class=main-img src="{{b.pics[0]}}">{% if b.video %}<video controls src="/uploads/{{b.video}}" style="width:100%;height:120px;background:#000"></video>{% endif %}<div class=thumbs>{% for t in b.pics[1:5] %}<img src="{{t}}" onclick="ch({{b.id}},'{{t}}')">{% endfor %}</div><div class=body><div style="font-size:11px;color:#888">{{b.cat}} • {{b.town}}</div><div style="font-size:13px;font-weight:700;line-height:1.3">{{b.name}} - {{b.description}}</div><div style="color:#FFA41C;font-size:13px">★★★★★ <span style="color:#007185;font-size:11px">(128)</span></div><div class=price><sup style="font-size:12px">MK</sup> <b>{{b.price}}</b> <s>MK 40,000</s></div><div class=prime>✓ prime FREE delivery</div><div style="font-size:11px;color:#666">Delivery to <b>{{b.town}}, {{b.district}}</b></div><div class=stock>● In Stock - NEW STOCK</div><a class=btn-buy href="https://wa.me/{{b.whatsapp}}?text=Hi, I want to buy." target=_blank>Buy Now</a><a class=btn-wa href="https://wa.me/{{b.whatsapp}}?text=Hi, I found you on Bizworld." target=_blank>💬 Order on WhatsApp</a>{% if is_admin %}<a href="/delete/{{b.id}}?pw={{pw}}" style="color:red;font-size:11px">Remove</a> <a href="/promote/{{b.id}}?pw={{pw}}" style="font-size:11px">Promote</a>{% endif %}</div></div>{% endfor %}</div>
<div style="text-align:center;padding:18px;background:#131921;color:#fff;margin:14px;border-radius:18px"><b style="font-size:17px">Want your business here?</b><br><span style="color:#ccc;font-size:13px">Reach 1000s of customers in Malawi</span><br><br><a href=/add style="background:#FFD814;color:#111;padding:12px 22px;border-radius:25px;font-weight:800;display:inline-block">List Your Business FREE →</a></div>
<div class=bottom><a href=/ class=active><b>🏠</b>Home</a><a href="/?category=Salon & Cosmetics"><b>💇‍♀️</b>Beauty</a><a href="/?category=Food"><b>🍔</b>Food</a><a href=/add><b>＋</b>Sell</a><a href="https://wa.me/{{owner}}"><b>💬</b>Help</a></div>
"""
ADD = CSS + """
<div style="background:#131921;color:#fff;padding:22px;text-align:center;border-radius:0 0 20px 20px"><h2 style="margin:0">Sell on Bizworld</h2><p style="color:#FFD814">Add photos + video - Reach Malawi</p></div>
<div style="padding:16px;background:#fff;margin:12px;border-radius:18px"><form method=POST enctype="multipart/form-data">
<input name=name placeholder="Product / Business Name" required>
<select name=category required>{% for c in categories %}<option>{{c}}</option>{% endfor %}</select>
<select name=district required>{% for d in districts %}<option>{{d}}</option>{% endfor %}</select>
<input name=town placeholder="Town e.g Chileka" required>
<input name=phone placeholder="WhatsApp e.g 0993066515" required>
<input name=price placeholder="Price e.g 15000" required>
<textarea name=description placeholder="Describe your product" required></textarea>
<input name=products placeholder="Products e.g Hair, Nails">
<label><b>📸 Photos (Select up to 5)</b></label><input type=file name=photos accept="image/*" multiple>
<label><b>🎥 Video (1 video)</b></label><input type=file name=video accept="video/*">
<button class=submit>List My Product →</button></form><br><a href=/>← Back to Home</a></div>
"""
@app.route("/")
def home():
    district = request.args.get("district","All")
    cat = request.args.get("category","All")
    q = request.args.get("q","").strip()
    pw = request.args.get("pw","")
    c = db()
    sql = "SELECT * FROM businesses WHERE 1=1"
    p = []
    if district != "All":
        sql += " AND district=?"
        p.append(district)
    if cat != "All":
        sql += " AND category=?"
        p.append(cat)
    if q:
        sql += " AND (name LIKE ? OR description LIKE ?)"
        like = "%" + q + "%"
        p += [like, like]
    sql += " ORDER BY promoted DESC"
    rows = c.execute(sql, p).fetchall()
    c.close()
    biz = []
    for r in rows:
        d = dict(r)
        d["pics"] = getpics(r)
        d["cat"] = SHORT.get(d["category"], d["category"])
        if not d["price"]:
            d["price"] = "5000"
        biz.append(d)
    return render_template_string(HOME, businesses=biz, districts=["All"]+DISTRICTS, categories=["All"]+CATEGORIES, district=district, cat=cat, q=q, pw=pw, is_admin=(pw==ADMIN_PASSWORD), owner=OWNER, cat_short=SHORT, emoji=EMOJI)
@app.route("/add", methods=["GET","POST"])
def add():
    if request.method == "POST":
        photos = []
        for f in request.files.getlist("photos"):
            s = save(f, {"png","jpg","jpeg","webp","gif"})
            if s:
                photos.append(s)
        video = save(request.files.get("video"), {"mp4","mov","webm","3gp"})
        phone = request.form["phone"]
        c = db()
        c.execute("INSERT INTO businesses (name,category,district,town,phone,whatsapp,description,products,photo,video,photos,price) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (request.form["name"], request.form["category"], request.form["district"], request.form["town"], phone, towa(phone), request.form["description"], request.form["products"], photos[0] if photos else "", video, json.dumps(photos), request.form.get("price","")))
        c.commit()
        c.close()
        return redirect("/")
    return render_template_string(ADD, categories=CATEGORIES, districts=DISTRICTS)
@app.route("/delete/<int:bid>")
def delete(bid):
    if request.args.get("pw") != ADMIN_PASSWORD:
        return "Wrong password"
    c = db()
    c.execute("DELETE FROM businesses WHERE id=?", (bid,))
    c.commit()
    c.close()
    return redirect("/?pw=" + ADMIN_PASSWORD)
@app.route("/promote/<int:bid>")
def promote(bid):
    if request.args.get("pw") != ADMIN_PASSWORD:
        return "Wrong password"
    c = db()
    cur = c.execute("SELECT promoted FROM businesses WHERE id=?", (bid,)).fetchone()
    if cur:
        c.execute("UPDATE businesses SET promoted=? WHERE id=?", (0 if cur[0] else 1, bid))
        c.commit()
    c.close()
    return redirect("/?pw=" + ADMIN_PASSWORD)
@app.route("/uploads/<name>")
def up(name):
    return send_from_directory("uploads", name)
@app.route("/manifest.json")
def man():
    m = {"name":"Bizworld Malawi","short_name":"Bizworld","start_url":"/","display":"standalone","background_color":"#ffffff","theme_color":"#131921","icons":[{"src":"/icon-192.png","sizes":"192x192","type":"image/png"},{"src":"/icon-512.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}]}
    return Response(json.dumps(m), mimetype="application/manifest+json")
@app.route("/sw.js")
def sw():
    js = "self.addEventListener('install', e => { self.skipWaiting(); }); self.addEventListener('activate', e => { self.clients.claim(); }); self.addEventListener('fetch', e => { e.respondWith(fetch(e.request).catch(() => caches.match(e.request))); });"
    return Response(js, mimetype="application/javascript")
@app.route("/icon-192.png")
def i1():
    if os.path.exists("icon-192.png"):
        return send_from_directory(".", "icon-192.png")
    return Response(make_png(192), mimetype="image/png")
@app.route("/icon-512.png")
def i2():
    if os.path.exists("icon-512.png"):
        return send_from_directory(".", "icon-512.png")
    return Response(make_png(512), mimetype="image/png")
if __name__ == "__main__":
    app.run(debug=True)
