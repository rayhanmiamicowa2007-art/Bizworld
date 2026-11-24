from flask import Flask, request, redirect, url_for, render_template_string
from urllib.parse import quote

app = Flask(__name__)

# --- Sample Businesses in Lilongwe ---
BUSINESSES = [
    {"name": "Lilongwe Fresh Foods", "category": "Food", "desc": "Fresh vegetables, fruits & groceries delivered in Area 47.", "price": "From K2,000", "phone": "265880123456", "location": "Area 47, Lilongwe", "featured": True},
    {"name": "Glow Beauty Salon", "category": "Beauty", "desc": "Braiding, nails, makeup & wigs. Walk-ins welcome.", "price": "From K5,000", "phone": "265991234567", "location": "Old Town, Lilongwe", "featured": True},
    {"name": "TechFix Malawi", "category": "Phones", "desc": "Phone repair, screens, batteries & accessories in 30 mins.", "price": "From K10,000", "phone": "265882345678", "location": "City Centre, Lilongwe", "featured": False},
    {"name": "Urban Styles Boutique", "category": "Fashion", "desc": "Latest fashion, shoes & bags for men & women.", "price": "From K15,000", "phone": "265993456789", "location": "Area 25, Lilongwe", "featured": False},
    {"name": "HomeClean Services", "category": "Services", "desc": "House cleaning, laundry & fumigation. Book same day.", "price": "From K20,000", "phone": "265884567890", "location": "All Lilongwe", "featured": False},
    {"name": "Mama's Kitchen", "category": "Food", "desc": "Nsima, Chambo, Beef & local dishes. Lunch delivery.", "price": "From K4,500", "phone": "265995678901", "location": "Area 18, Lilongwe", "featured": False},
]

CATEGORIES = ["All", "Food", "Fashion", "Beauty", "Phones", "Services"]

BASE_STYLE = """
<style>
* {box-sizing:border-box; font-family: 'Segoe UI', Arial, sans-serif;}
body {margin:0; background:#f6f7fb; color:#111;}
header {background:#0f172a; color:white; padding:28px 16px; text-align:center;}
header h1 {margin:0; font-size:32px;}
header p {opacity:.85; margin:8px 0 16px;}
header a {background:#22c55e; color:white; padding:11px 18px; border-radius:999px; text-decoration:none; font-weight:700; display:inline-block;}
.search {max-width:900px; margin:-18px auto 0; background:white; padding:14px; border-radius:14px; box-shadow:0 8px 30px rgba(0,0,0,.1); display:flex; gap:8px; flex-wrap:wrap;}
.search input {flex:1; min-width:200px; padding:12px; border:1px solid #ddd; border-radius:10px;}
.search select, .search button {padding:12px; border-radius:10px; border:1px solid #ddd;}
.search button {background:#0f172a; color:white; border:none; font-weight:700;}
.cats {max-width:900px; margin:16px auto; padding:0 12px; display:flex; gap:8px; flex-wrap:wrap;}
.cats a {background:white; padding:8px 14px; border-radius:999px; text-decoration:none; color:#111; border:1px solid #e5e5e5;}
.cats a.active {background:#0f172a; color:white;}
.grid {max-width:900px; margin:0 auto; padding:12px; display:grid; grid-template-columns:1fr 1fr; gap:14px;}
@media(max-width:600px){.grid{grid-template-columns:1fr;}}
.card {background:white; border-radius:16px; padding:16px; box-shadow:0 4px 18px rgba(0,0,0,.06);}
.badge {display:inline-block; background:#e0f2fe; color:#0369a1; padding:4px 10px; border-radius:999px; font-size:12px; font-weight:700;}
.featured {background:#fef3c7; color:#92400e;}
.card h3 {margin:10px 0 6px;}
.card p {color:#555; font-size:14px; line-height:1.5;}
.price {font-weight:800; color:#16a34a;}
.wa {display:block; text-align:center; background:#22c55e; color:white; padding:12px; border-radius:10px; text-decoration:none; font-weight:800; margin-top:12px;}
footer {text-align:center; padding:24px; color:#777; font-size:13px;}
.form {max-width:600px; margin:20px auto; background:white; padding:20px; border-radius:16px;}
.form input, .form select, .form textarea {width:100%; padding:12px; margin:8px 0; border:1px solid #ddd; border-radius:10px;}
.form button {width:100%; padding:14px; background:#0f172a; color:white; border:none; border-radius:10px; font-weight:800;}
</style>
"""

@app.route('/')
def home():
    q = request.args.get('q', '').lower()
    cat = request.args.get('cat', 'All')
    filtered = BUSINESSES
    if cat != 'All':
        filtered = [b for b in filtered if b['category'] == cat]
    if q:
        filtered = [b for b in filtered if q in b['name'].lower() or q in b['desc'].lower() or q in b['location'].lower()]
    # Featured first
    filtered = sorted(filtered, key=lambda x: not x['featured'])

    cards = ""
    for b in filtered:
        wa_text = quote(f"Hi {b['name']}! I found you on Bizworld. I want to order / enquire.")
        feat = "<span class='badge featured'>⭐ Featured</span> " if b['featured'] else ""
        cards += f"""
        <div class='card'>
          {feat}<span class='badge'>{b['category']}</span>
          <h3>{b['name']}</h3>
          <p>{b['desc']}</p>
          <p>📍 {b['location']}<br><span class='price'>{b['price']}</span></p>
          <a class='wa' href='https://wa.me/{b['phone']}?text={wa_text}' target='_blank'>💬 Order on WhatsApp</a>
        </div>
        """
    if not cards:
        cards = "<p style='grid-column:1/-1; text-align:center;'>No businesses found. Try another search.</p>"

    cat_links = "".join([f"<a class='{'active' if c==cat else ''}' href='/?cat={c}'>{c}</a>" for c in CATEGORIES])

    return render_template_string(BASE_STYLE + f"""
    <header>
      <h1>🌍 Bizworld</h1>
      <p>Find the best businesses in Lilongwe. Order on WhatsApp.</p>
      <a href='/add'>+ Add Your Business - FREE</a>
    </header>
    <form class='search' method='get' action='/'>
      <input name='q' placeholder='Search e.g. food, salon, phone repair...' value='{request.args.get('q','')}'>
      <select name='cat'><option>All</option>{''.join([f"<option {'selected' if c==cat else ''}>{c}</option>" for c in CATEGORIES if c!='All'])}</select>
      <button>Search</button>
    </form>
    <div class='cats'>{cat_links}</div>
    <div class='grid'>{cards}</div>
    <footer>Bizworld • Lilongwe, Malawi • Businesses pay to be Featured • Made with ❤️ in Malawi</footer>
    """)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        BUSINESSES.insert(0, {
            "name": request.form.get('name'),
            "category": request.form.get('category'),
            "desc": request.form.get('desc'),
            "price": request.form.get('price'),
            "phone": request.form.get('phone').replace('+','').replace(' ',''),
            "location": request.form.get('location'),
            "featured": False
        })
        return redirect(url_for('home'))
    return render_template_string(BASE_STYLE + """
    <header><h1>+ Add Your Business</h1><p>Join Bizworld - get customers on WhatsApp</p></header>
    <form class='form' method='post'>
      <input name='name' placeholder='Business Name' required>
      <select name='category'><option>Food</option><option>Fashion</option><option>Beauty</option><option>Phones</option><option>Services</option></select>
      <textarea name='desc' placeholder='What do you sell? e.g. Fresh mandasi & tea' required></textarea>
      <input name='price' placeholder='Starting Price e.g. From K5,000' required>
      <input name='phone' placeholder='WhatsApp Number e.g. 265880123456' required>
      <input name='location' placeholder='Location e.g. Area 47, Lilongwe' required>
      <button>Publish My Business →</button>
    </form>
    <p style='text-align:center;'><a href='/'>← Back to Home</a></p>
    """)

if __name__ == '__main__':
    app.run(debug=True)
