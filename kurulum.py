import os
from flask import Flask, render_template, request

# --- 1. ADIM: GÖRSEL HAZIRLIK (İNŞAAT) ---
if not os.path.exists('templates'):
    os.makedirs('templates')

html_icerik = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Medistok Pro - Akıllı Stok Sistemi</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); width: 100%; max-width: 450px; text-align: center; }
        h1 { color: #1a202c; font-size: 24px; margin-bottom: 10px; }
        p { color: #718096; margin-bottom: 30px; }
        .search-form { display: flex; gap: 10px; margin-bottom: 20px; }
        input { flex: 1; padding: 12px; border: 2px solid #e2e8f0; border-radius: 10px; outline: none; transition: 0.3s; }
        input:focus { border-color: #3182ce; }
        button { background: #3182ce; color: white; border: none; padding: 12px 20px; border-radius: 10px; font-weight: 600; cursor: pointer; }
        .alert { padding: 15px; border-radius: 10px; margin-top: 20px; text-align: left; border-left: 6px solid; }
        .success { background: #f0fff4; border-color: #38a169; color: #2f855a; }
        .warning { background: #fffaf0; border-color: #dd6b20; color: #9c4221; }
        .error { background: #fff5f5; border-color: #e53e3e; color: #c53030; }
        .suggestion { font-size: 13px; margin-top: 8px; color: #4a5568; border-top: 1px solid rgba(0,0,0,0.05); padding-top: 5px; }
        .stock-badge { font-weight: bold; font-size: 1.1em; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🏥 Medistok Pro</h1>
        <p>Akıllı Envanter Terminali</p>
        <form action="/kontrol" method="post" class="search-form">
            <input type="text" name="ilac_adi" placeholder="Ürün ismini yazın..." required>
            <button type="submit">Sorgula</button>
        </form>
        {% if sonuc %}
            {% set alert_class = 'error' %}
            {% if durum %}
                {% if adet|int > 5 %} {% set alert_class = 'success' %}
                {% else %} {% set alert_class = 'warning' %} {% endif %}
            {% endif %}
            <div class="alert {{ alert_class }}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong>{{ sonuc }}</strong>
                    <span class="stock-badge">{{ adet if durum else '0' }} Adet</span>
                </div>
                {% if alert_class == 'warning' %} <div style="font-size: 12px; margin-top: 5px;">⚠️ <b>KRİTİK STOK:</b> Sipariş verilmeli.</div> {% endif %}
                {% if alert_class == 'error' %} <div style="font-size: 12px; margin-top: 5px;">🚫 <b>STOKTA YOK:</b> Tedarik gerekli.</div> {% endif %}
                {% if muadil %} <div class="suggestion">💡 <b>Muadil:</b> {{ muadil }}</div> {% endif %}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html_icerik)

# --- 2. ADIM: MOTOR VE TAM VERİ TABANI ---
app = Flask(__name__)

ILAC_REHBERI = {
    "Parol 500mg": {"stok": True, "muadil": "Arveles", "adet": 10},
    "Arveles 25mg": {"stok": False, "muadil": "Apranax", "adet": 0},
    "Augmentin 1000mg": {"stok": True, "muadil": "Klamer", "adet": 3},
    "Coraspin 100mg": {"stok": True, "muadil": "Ecopirin", "adet": 15},
    "Majezik 100mg": {"stok": False, "muadil": "Dex-Forte", "adet": 0},
    "Vicks VapoRub": {"stok": True, "muadil": "Peditus", "adet": 10},
    "Ventolin": {"stok": False, "muadil": "Airsalb", "adet": 0},
    "Apranax Fort": {"stok": True, "muadil": "Naprosyn", "adet": 8},
    "Dolorex 50mg": {"stok": True, "muadil": "Cataflam", "adet": 12},
    "Glifor 1000mg": {"stok": True, "muadil": "Matofin", "adet": 20},
    "Lansor 30mg": {"stok": False, "muadil": "Aprazol", "adet": 0},
    "Buscopan Plus": {"stok": True, "muadil": "Spazmol", "adet": 7},
    "Nexium 40mg": {"stok": True, "muadil": "Esopro", "adet": 5},
    "Aprol 550mg": {"stok": True, "muadil": "Apranax", "adet": 10},
    "Dex-Forte": {"stok": False, "muadil": "Arveles", "adet": 0},
    "Klamer 500mg": {"stok": True, "muadil": "Augmentin", "adet": 4},
    "Amoklavin BID": {"stok": True, "muadil": "Augmentin", "adet": 10},
    "Panadol": {"stok": True, "muadil": "Parol", "adet": 15},
    "Gaviscon Likit": {"stok": True, "muadil": "Rennie", "adet": 6},
    "Rennie Tablet": {"stok": True, "muadil": "Talcid", "adet": 9},
    "Benical Cold": {"stok": False, "muadil": "A-Ferin", "adet": 0},
    "A-Ferin Forte": {"stok": True, "muadil": "Tylol Hot", "adet": 11},
    "Tylol Hot": {"stok": True, "muadil": "A-Ferin", "adet": 8},
    "Nurofen Cold": {"stok": True, "muadil": "Dolven", "adet": 13},
    "Dolven Şurup": {"stok": True, "muadil": "Calpol", "adet": 2},
    "Calpol 6 Plus": {"stok": True, "muadil": "Dolven", "adet": 10},
    "Bepanthol": {"stok": True, "muadil": "Hametan", "adet": 25},
    "Hametan Krem": {"stok": True, "muadil": "Bepanthol", "adet": 15},
    "Fucidin Krem": {"stok": False, "muadil": "Terramycin", "adet": 0},
    "Terramycin": {"stok": True, "muadil": "Fucidin", "adet": 5},
    "Voltaren Emulgel": {"stok": True, "muadil": "Dikloron", "adet": 10},
    "Dikloron Jel": {"stok": True, "muadil": "Voltaren", "adet": 8},
    "Advante Krem": {"stok": True, "muadil": "Momecon", "adet": 10},
    "Momecon Pomat": {"stok": True, "muadil": "Elocon", "adet": 7},
    "Elocon Krem": {"stok": True, "muadil": "Momecon", "adet": 12},
    "Aerius 5mg": {"stok": False, "muadil": "Deloday", "adet": 0},
    "Deloday 5mg": {"stok": True, "muadil": "Aerius", "adet": 10},
    "Zyrtec Tablet": {"stok": True, "muadil": "Allerset", "adet": 15},
    "Allerset Damla": {"stok": True, "muadil": "Zyrtec", "adet": 6},
    "Xyzal 5mg": {"stok": True, "muadil": "Crebros", "adet": 4},
    "Crebros 5mg": {"stok": True, "muadil": "Xyzal", "adet": 9},
    "Davit-3": {"stok": True, "muadil": "Devit-3", "adet": 20},
    "Devit-3 Ampul": {"stok": True, "muadil": "Davit-3", "adet": 10},
    "Euthyrox 50mcg": {"stok": True, "muadil": "Levotiron", "adet": 11},
    "Levotiron 50mcg": {"stok": False, "muadil": "Euthyrox", "adet": 0},
    "Saneloc 50mg": {"stok": True, "muadil": "Beloc", "adet": 10},
    "Beloc ZOK 50mg": {"stok": True, "muadil": "Saneloc", "adet": 8},
    "Co-Diovan": {"stok": True, "muadil": "Karvezea", "adet": 5},
    "Lipitor 20mg": {"stok": True, "muadil": "Ator", "adet": 10},
    "Ator 20mg": {"stok": True, "muadil": "Lipitor", "adet": 14}
}

@app.route('/')
def ana_sayfa():
    return render_template('index.html')

@app.route('/kontrol', methods=['POST'])
def kontrol():
    aranan = request.form.get('ilac_adi', '').strip()
    # Küçük/Büyük harf duyarsız arama
    bulunan = next((k for k in ILAC_REHBERI if aranan.lower() in k.lower()), None)
    
    if bulunan:
        bilgi = ILAC_REHBERI[bulunan]
        return render_template('index.html', 
                               sonuc=bulunan, 
                               durum=bilgi['stok'], 
                               muadil=bilgi['muadil'], 
                               adet=bilgi['adet'])
    
    return render_template('index.html', sonuc="Bulunamadı", durum=False, adet=0)

if __name__ == '__main__':
    print("✅ TÜM VERİLER YÜKLENDİ!")
    print("🚀 SİSTEM 5001 PORTUNDA ÇALIŞIYOR...")
    app.run(debug=True, port=5001)