import json
from flask import Flask, render_template, request
from difflib import get_close_matches

app = Flask(__name__)
JSON_DOSYASI = 'ilaclar.json'

def veriyi_oku():
    try:
        with open(JSON_DOSYASI, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

@app.route('/')
def ana_sayfa():
    return render_template('index.html')

@app.route('/kontrol', methods=['POST'])
def kontrol():
    ilaclar = veriyi_oku()
    aranan = request.form.get('ilac_adi', '').strip()
    
    if not aranan: return render_template('index.html')
    
    # 1. Tam veya Kısmi Eşleşme
    bulunan = next((k for k in ilaclar if aranan.lower() in k.lower()), None)
    
    if bulunan:
        b = ilaclar[bulunan]
        return render_template('index.html', sonuc=bulunan, durum=b['stok'], muadil=b['muadil'], adet=int(b['adet']))
    
    # 2. Hata Toleranslı Öneri
    yakin_esyalar = get_close_matches(aranan, ilaclar.keys(), n=1, cutoff=0.4)
    if yakin_esyalar:
        return render_template('index.html', sonuc=f"'{aranan}' bulunamadı.", onerilen=yakin_esyalar[0])
    
    return render_template('index.html', sonuc="Bulunamadı", durum=False, adet=0)

@app.route('/stok_guncelle', methods=['POST'])
def stok_guncelle():
    ilaclar = veriyi_oku()
    ilac_adi = request.form.get('ilac_adi')
    yeni_adet = request.form.get('yeni_adet')

    if ilac_adi in ilaclar and yeni_adet:
        yeni_adet_int = int(yeni_adet)
        ilaclar[ilac_adi]['adet'] = yeni_adet_int
        # Adet 0'dan büyükse stok var (True), değilse yok (False) yap
        ilaclar[ilac_adi]['stok'] = (yeni_adet_int > 0)
        
        with open(JSON_DOSYASI, 'w', encoding='utf-8') as f:
            json.dump(ilaclar, f, ensure_ascii=False, indent=4)
            
    # Güncelleme sonrası veriyi tekrar gönder
    return render_template('index.html', sonuc=ilac_adi, durum=ilaclar[ilac_adi]['stok'], muadil=ilaclar[ilac_adi]['muadil'], adet=yeni_adet_int)

if __name__ == '__main__':
    app.run(debug=True, port=5001)