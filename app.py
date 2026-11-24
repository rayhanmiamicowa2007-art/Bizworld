from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string("""
    <h1 style='text-align:center; font-family:sans-serif; margin-top:100px;'>
    🌍 Welcome to Bizworld
    </h1>
    <p style='text-align:center;'>Your business world is live!</p>
    """)

if __name__ == '__main__':
    app.run(debug=True)
