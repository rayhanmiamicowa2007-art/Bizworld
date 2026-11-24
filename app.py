from flask import Flask, request, redirect, url_for, render_template_string
from urllib.parse import quote
import json, os

app = Flask(__name__)
DATA_FILE = "businesses.json"
ADMIN_PIN = "1995"  # CHANGE to your PIN
OWNER_PHONE = "265986765421" # CHANGE to YOUR WhatsApp

DEFAULT = [
    {"name": "Lilongwe Fresh Foods", "category": "Food", "city": "Lilongwe", "desc": "Fresh vegetables, fruits & groceries delivered in Area 47.", "price": "From K2,000", "phone": "265880123456", "location": "Area 47, Lilongwe", "featured": True, "image": ""},
    {"name": "Glow Beauty Salon", "category": "Beauty", "city": "Lilongwe", "desc": "Braiding, nails, makeup & wigs. Walk-ins welcome.", "price": "From K5,000", "phone": "265991234567", "location": "Old Town, Lilongwe", "featured": True, "image": ""},
    {"name": "TechFix Malawi", "category": "Phones", "city": "Lilongwe", "desc": "Phone repair, screens, batteries & accessories in 30 mins.", "price": "From K10,000", "phone": "265882345678", "location": "City Centre, Lilongwe", "featured": False, "image": ""},
    {"name": "Urban Styles Boutique", "category": "Fashion", "city": "Blantyre", "desc": "Latest fashion, shoes & bags for men & women.", "price": "From K15,000", "phone": "265993456789", "location": "Chichiri, Blantyre", "featured": False, "image": ""},
    {"name": "HomeClean Services", "category": "Services", "city": "Blantyre", "desc": "House cleaning, laundry & fumigation. Book same day.", "price": "From K20,000", "phone": "265884567890", "location": "All Blantyre", "featured": False, "image": ""},
    {"name": "Mama's Kitchen", "category": "Food", "city": "Lilongwe", "desc": "Nsima, Chambo, Beef & local dishes. Lunch delivery.", "price": "From K4,500", "phone": "265995678901", "location": "Area 18, Lilongwe", "featured": False, "image": ""},
]

def load():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                data = json.load(f)
                # Add city to old businesses that don't have it
                for b in data:
                    if "city" not in b: b["city"] = "Lilongwe"
                return data
        except: return DEFAULT.copy()
    return DEFAULT.copy()
def save(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

BUSINESSES = load()
CATEGORIES = ["All", "Food", "Fashion", "Beauty", "Phones", "Services"]
CITIES = ["All", "Lilongwe", "Blantyre", "Mzuzu", "Zomba", "Mzimba"]
EMOJI = {"Food": "🍲", "Fashion": "👗", "Beauty": "💅", "Phones": "📱", "Services": "🧹"}

STYLE = """
<style>
* {box-sizing:border-box; font-family:'Segoe UI',Arial,sans-serif;}
body {margin:0; background:#f6f7fb; color:#111;}
header {background:#0f172a; color:white; padding:28px 16px; text-align:center;}
header h1 {margin:0; font-size:32px;} header p {opacity:.85; margin:8px 0 16px;}
header a {background:#22c55e; color:white; padding:11px 18px; border-radius:999px; text-decoration:none; font-weight:700; display:inline-block; margin:4px;}
header a.gold {background:#f59e0b; color:#111;}
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
.card-img {height:160px; background:#e0e7ff; display:flex; align-items:center; justify-content:center; font-size:60px; overflow:hidden;}
.card-img img {width:100%; height:100%; object-fit:cover;}
.card-body {padding:16px;}
.badge {display:inline-block; background:#e0f2fe; color:#0369a1; padding:4px 10px; border-radius:999px; font-size:12px; font-weight:700;}
.badge-city {background:#dcfce7; color:#166534;}
.featured {background:#fef3c7; color:#92400e;}
.card h3 {margin:10px 0 6px;} .card p {color:#555; font-size:14px; line-height:1.5;}
.price {font-weight:800; color:#16a34a;}
.wa {display:block; text-align:center; background:#22c55e; color:white; padding:12px; border-radius:10px; text-decoration:none; font-weight:800; margin-top:12px;}
.del {position:absolute; top:8px; right:8px; background:#ef4444; color:white; border-radius:50%; width:28px; height:28px; text-align:center; line-height:28px; text-decoration:none; font-weight:800;}
footer {text-align:center; padding:24px; color:#777; font-size:13px;}
.form {max-width:600px; margin:20px auto; background:white; padding:20px; border-radius:16px;}
.form input, .form select, .form textarea {width:100%; padding:12px; margin:8px 0; border:1px solid #ddd; border-radius:10px;}
.form button {width:100%; padding:14px; background:#0f172a; color:white; border:none; border-radius:10px; font-weight:800;}
.plan {background:white; border-radius:16px; padding:20px; margin:12px 0; border:2px solid #eee;}
.plan.hot {border-color:#f59e0b; background:#fffbeb;}
small {color:#888;}
</style>
"""

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
    indexed = sorted(indexed, key=lambda x: not x[1].get('featured', False))
    cards=""
    for idx, b in indexed:
        wa_text = quote(f"Hi {b['name']}! I found you on Bizworld. I want to order / enquire.")
        feat = "<span class='badge featured'>⭐ Featured</span> " if b.get('featured') else ""
        img = f"<img src='{b.get('image','')}'>" if b.get('image') else EMOJI.get(b['category'],'🏪')
        delbtn = f"<a class='del' href='/delete/{idx}'>×</a>" if admin else ""
        cards += f"""<div class='card'>{delbtn}<div class='card-img'>{img}</div><div class='card-body'>{feat}<span class='badge'>{b['category']}</span> <span class='badge badge-city'>📍 {b.get('city','Lilongwe')}</span><h3>{b['name']}</h3><p>{b['desc']}</p><p>📍 {b['location']}<br><span class='price'>{b['price']}</span></p><a class='wa' href='https://wa.me/{b['phone']}?text={wa_text}' target='_blank'>💬 Order on WhatsApp</a></div></div>"""
    if not cards: cards="<p style='grid-column:1/-1; text-align:center;'>No businesses found in this city. Try another city.</p>"
    cat_links="".join([f"<a class='{'active' if c==cat else ''}' href='/?cat={c}&city={city}'>{c}</a>" for c in CATEGORIES])
    city_links="".join([f"<a class='{'city-active' if c==city else ''}' href='/?city={c}&cat={cat}'>📍 {c}</a>" for c in CITIES])
    return render_template_string(STYLE+f"""
    <header><h1>🌍 Bizworld</h1><p>Find the best businesses in Malawi. Order on WhatsApp.</p><a href='/add'>+ Add Your Business - FREE</a><a class='gold' href='/featured'>⭐ Promote My Business</a></header>
    <form class='search' method='get' action='/'><input name='q' placeholder='Search e.g. food, salon, phone repair...' value='{request.args.get('q','')}'><select name='city'><option>All</option>{''.join([f"<option {'selected' if c==city else ''}>{c}</option>" for c in CITIES if c!='All'])}</select><select name='cat'><option>All</option>{''.join([f"<option {'selected' if c==cat else ''}>{c}</option>" for c in CATEGORIES if c!='All'])}</select><button>Search</button></form>
    <div class='cats'>{city_links}</div><div class='cats'>{cat_links}</div><div class='grid'>{cards}</div>
    <footer>Bizworld • Malawi 🇲🇼 • Lilongwe | Blantyre | Mzuzu | Zomba • <a href='/?admin=1'>Admin</a></footer>""")

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method=='POST':
        BUSINESSES.insert(0, {"name": request.form.get('name'), "category": request.form.get('category'), "city": request.form.get('city'), "desc": request.form.get('desc'), "price": request.form.get('price'), "phone": request.form.get('phone').replace('+','').replace(' ',''), "location": request.form.get('location'), "featured": False, "image": request.form.get('image','').strip()})
        save(BUSINESSES); return redirect(url_for('home'))
    return render_template_string(STYLE+"""
    <header><h1>+ Add Your Business</h1><p>Join Bizworld Malawi - get customers on WhatsApp</p></header>
    <form class='form' method='post'><input name='name' placeholder='Business Name' required><select name='city'><option>Lilongwe</option><option>Blantyre</option><option>Mzuzu</option><option>Zomba</option><option>Mzimba</option><option>Other</option></select><select name='category'><option>Food</option><option>Fashion</option><option>Beauty</option><option>Phones</option><option>Services</option></select><textarea name='desc' placeholder='What do you sell?' required></textarea><input name='price' placeholder='Starting Price e.g. From K5,000' required><input name='phone' placeholder='WhatsApp Number e.g. 265880123456 - YOUR number, customers will message YOU' required><input name='location' placeholder='Location e.g. Chichiri, Blantyre' required><input name='image' placeholder='Photo Link (optional)'><small>Your WhatsApp number is used for the green Order button. Customers message YOU directly.</small><button>Publish My Business →</button></form><p style='text-align:center;'><a href='/'>← Back to Home</a></p>""")

@app.route('/featured')
def featured():
    wa1 = quote("Hi Bizworld! I want FEATURED - 1 Week for K5,000. My business name is:")
    wa2 = quote("Hi Bizworld! I want FEATURED - 1 Month for K15,000. My business name is:")
    wa3 = quote("Hi Bizworld! I want TOP SPOT - 1 Month for K25,000. My business name is:")
    return render_template_string(STYLE+f"""
    <header><h1>⭐ Promote Your Business</h1><p>Get more customers in YOUR city. Be at the top.</p></header>
    <div style='max-width:600px; margin:20px auto; padding:0 12px;'>
      <div class='plan'><h3>⭐ Featured - 1 Week - K5,000</h3><p>✅ Yellow ⭐ Featured badge<br>✅ Show at top of homepage<br>✅ Show at top of your city</p><a class='wa' href='https://wa.me/{OWNER_PHONE}?text={wa1}'>Pay via WhatsApp →</a></div>
      <div class='plan hot'><h3>🔥 Featured - 1 Month - K15,000 <span class='badge'>MOST POPULAR</span></h3><p>✅ Everything in 1 Week<br>✅ Full month at top<br>✅ Best value</p><a class='wa' href='https://wa.me/{OWNER_PHONE}?text={wa2}'>Pay via WhatsApp →</a></div>
      <div class='plan'><h3>👑 Top Spot - 1 Month - K25,000</h3><p>✅ Very first card on homepage<br>✅ For 1 business only</p><a class='wa' href='https://wa.me/{OWNER_PHONE}?text={wa3}'>Pay via WhatsApp →</a></div>
      <div style='background:white; padding:16px; border-radius:12px;'><h3>How to pay:</h3><p>1. Tap Pay via WhatsApp<br>2. Send Airtel Money / TNM Mpamba to owner<br>3. Send screenshot<br>4. We make you Featured in 10 mins!</p></div>
      <p style='text-align:center;'><a href='/'>← Back to Home</a></p>
    </div>""")

@app.route('/delete/<int:idx>', methods=['GET','POST'])
def delete(idx):
    if request.method=='POST':
        if request.form.get('pin') == ADMIN_PIN and 0 <= idx < len(BUSINESSES):
            name = BUSINESSES[idx]['name']; del BUSINESSES[idx]; save(BUSINESSES)
            return f"<h2 style='text-align:center; font-family:Arial;'>Deleted {name} ✅<br><a href='/?admin=1'>Back</a></h2>"
        return "<h2 style='text-align:center;'>Wrong PIN ❌ <a href='/'>Back</a></h2>"
    if idx >= len(BUSINESSES): return redirect('/')
    return render_template_string(STYLE+f"""
    <header><h1>🗑️ Delete Business?</h1></header>
    <form class='form' method='post'><p>Are you sure you want to delete <b>{BUSINESSES[idx]['name']}</b>?</p><input name='pin' type='password' placeholder='Enter Admin PIN' required><button style='background:#ef4444;'>Yes, Delete</button></form><p style='text-align:center;'><a href='/?admin=1'>Cancel</a></p>""")

if __name__=='__main__':
    app.run(debug=True)
