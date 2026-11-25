from flask import Flask, request, render_template_string, redirect, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3, os, uuid, json
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs("uploads", exist_ok=True)
ADMIN_PASSWORD = "1995"
OWNER = "265986765421"
DISTRICTS = ["Blantyre","Lilongwe","Mzuzu","Zomba","Mzimba","Kasungu","Mangochi","Karonga","Salima","Dedza","Other"]
CATEGORIES = ["Salon & Cosmetics","Electronics & Phones","Food","Fashion & Clothes","Phones & Accessories","Grocery & Shops","Services","Other"]
SHORT = {"Salon & Cosmetics":"Beauty","Electronics & Phones":"Electronics","Food":"Food","Fashion & Clothes":"Fashion","Phones & Accessories":"Phones","Grocery & Shops":"Grocery","Services":"Services","Other":"Other"}
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
CSS = "<style>*{box-sizing:border-box}body{font-family:Arial;margin:0;background:#EAEDED;padding-bottom:70px}a{text-decoration:none}.top{background:#131921;color:#fff;padding:10px;position:sticky;top:0;z-index:20}.logo{font-size:22px;font-weight:900}.logo span{color:#FF9900}.search{display:flex;margin-top:10px;background:#fff;border-radius:8px;overflow:hidden;height:42px}.search input{flex:1;border:none;outline:none;padding:0 10px}.search button{background:#FEBD69;border:none;padding:0 14px;font-weight:bold}.install{background:#FFD814;padding:11px;text-align:center;font-weight:bold;display:none;cursor:pointer}.hero{background:#FFD814;padding:14px;text-align:center}.btn-sell{background:#FFD814;border:1px solid #FCD200;padding:10px 18px;border-radius:20px;font-weight:bold;color:#111;display:inline-block}.btn-prime{background:#131921;color:#fff;padding:10px 18px;border-radius:20px;font-weight:bold;display:inline-block}.grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:10px}.card{background:#fff;border-radius:8px;overflow:hidden}.main-img{width:100%;height:165px;object-fit:cover}.thumbs{display:flex;gap:4px;padding:6px}.thumbs img{width:30px;height:30px;object-fit:cover;border-radius:4px}.body{padding:8px}.price b{font-size:19px}.btn-buy{background:#FFD814;width:100%;padding:11px;border-radius:20px;font-weight:bold;display:block;text-align:center;color:#111}.btn-wa{background:#25D366;color:#fff;width:100%;padding:11px;border-radius:20px;font-weight:bold;margin-top:6px;display:block;text-align:center}.bottom{position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid #ddd;display:flex;justify-content:space-around;padding:8px 0;z-index:30}.bottom a{text-align:center;font-size:10px;color:#565959}input,select,textarea{width:100%;padding:13px;margin:7px 0;border-radius:8px;border:1px solid #ccc}.submit{width:100%;padding:14px;background:#FFD814;border-radius:20px;font-weight:bold}.preview img,.preview video{width:80px;height:80px;object-fit:cover;border-radius:8px}</style><link rel=manifest href=/manifest.json><meta name=theme-color content=#131921><meta name=mobile-web-app-capable content=yes><meta name=apple-mobile-web-app-capable content=yes><link rel=apple-touch-icon href=/icon-192.png>"
HOME = CSS + """
<div class=top><div class=logo>bizworld<span>.mw</span></div><form method=GET action=/ class=search><input name=q value="{{q}}" placeholder="Search Bizworld..."><input type=hidden name=district value="{{district}}"><input type=hidden name=pw value="{{pw}}"><button>Go</button></form></div>
<div class=install id=installBar onclick=doInstall()>Install Bizworld App - Like WhatsApp - Tap Here</div>
<script>let dp;window.addEventListener("beforeinstallprompt",function(e){e.preventDefault();dp=e;document.getElementById("installBar").style.display="block";});function doInstall(){if(dp){dp.prompt();}else{alert("Android: Tap 3 dots - Install app. iPhone: Share - Add to Home Screen");}}if("serviceWorker" in navigator){navigator.serviceWorker.register("/sw.js");}function ch(id,s){document.getElementById("m"+id).src=s;}</script>
<div class=hero><h2 style="margin:0">Shop in Malawi - Order on WhatsApp</h2><br><a class=btn-sell href=/add>+ Sell - FREE</a> <a class=btn-prime href="https://wa.me/{{owner}}?text=Hi Bizworld, I want to PROMOTE">Promote</a></div>
<div style="padding:8px;font-size:12px">Filter: {% for d in districts %}<a href="/?district={{d}}&category={{cat}}&pw={{pw}}">{{d}}</a> - {% endfor %}</div>
<div class=grid>{% for b in businesses %}<div class=card><img id="m{{b.id}}" class=main-img src="{{b.pics[0]}}">{% if b.video %}<video controls src="/uploads/{{b.video}}" style="width:100%;height:120px;background:#000"></video>{% endif %}<div class=thumbs>{% for t in b.pics[1:5] %}<img src="{{t}}" onclick="ch({{b.id}},'{{t}}')">{% endfor %}</div><div class=body><div>{{b.cat}}</div><div>{{b.name}} - {{b.description}}</div><div class=price><b>MK {{b.price}}</b></div><div>Delivery to <b>{{b.town}}, {{b.district}}</b></div><div style="color:#007600">In Stock - NEW STOCK</div><a class=btn-buy href="https://wa.me/{{b.whatsapp}}?text=Hi, I want to buy." target=_blank>Buy Now</a><a class=btn-wa href="https://wa.me/{{b.whatsapp}}?text=Hi, I found you on Bizworld." target=_blank>Order on WhatsApp</a>{% if is_admin %}<a href="/delete/{{b.id}}?pw={{pw}}" style="color:red;font-size:11px">Remove</a> <a href="/promote/{{b.id}}?pw={{pw}}" style="font-size:11px">Promote</a>{% endif %}</div></div>{% endfor %}</div>
<div class=bottom><a href=/>Home</a><a href="/?category=Salon & Cosmetics">Beauty</a><a href="/?category=Food">Food</a><a href=/add>Sell</a><a href="https://wa.me/{{owner}}">Help</a></div>
"""
ADD = CSS + """
<div style="background:#131921;color:#fff;padding:16px;text-align:center"><h2>Sell on Bizworld</h2></div>
<div style="padding:16px;background:#fff"><form method=POST enctype="multipart/form-data">
<input name=name placeholder="Product / Business Name" required>
<select name=category required>{% for c in categories %}<option>{{c}}</option>{% endfor %}</select>
<select name=district required>{% for d in districts %}<option>{{d}}</option>{% endfor %}</select>
<input name=town placeholder="Town e.g Chileka" required>
<input name=phone placeholder="WhatsApp e.g 0993066515" required>
<input name=price placeholder="Price e.g 15000" required>
<textarea name=description placeholder="Describe your product" required></textarea>
<input name=products placeholder="Products e.g Hair, Nails">
<label><b>Photos (Select up to 5)</b></label><input type=file name=photos accept="image/*" multiple>
<label><b>Video (1 video)</b></label><input type=file name=video accept="video/*">
<button class=submit>List My Product</button></form><br><a href=/>Back</a></div>
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
    return render_template_string(HOME, businesses=biz, districts=["All"]+DISTRICTS, categories=["All"]+CATEGORIES, district=district, cat=cat, q=q, pw=pw, is_admin=(pw==ADMIN_PASSWORD), owner=OWNER)
@app.route("/add", methods=["GET","POST"])
def add():
    if request.method == "POST":
        photos = []
        for f in request.files.getlist("photos"):
            s = save(f, ALLOWED_IMG)
            if s:
                photos.append(s)
        video = save(request.files.get("video"), ALLOWED_VIDEO)
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
    return send_from_directory(".", "manifest.json", mimetype="application/manifest+json")
@app.route("/sw.js")
def sw():
    return send_from_directory(".", "sw.js", mimetype="application/javascript")
@app.route("/icon-192.png")
def i1():
    return send_from_directory(".", "icon-192.png")
@app.route("/icon-512.png")
def i2():
    return send_from_directory(".", "icon-512.png")
if __name__ == "__main__":
    app.run(debug=True)
