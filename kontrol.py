from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client
from difflib import get_close_matches

app = Flask(__name__)

# Supabase bilgilerin
URL = "https://haaoborfpaexelqmgmkx.supabase.co"
KEY = "sb_publishable_SFMcmpXgybgVEFBgQApyKQ_39O_Lq3i"

supabase = create_client(URL, KEY)

@app.route('/')
def ana_sayfa():
    return render_template('index.html')

@app.route('/kontrol', methods=['POST'])
def kontrol():
    aranan = request.form.get('ilac_adi', '').strip()
    if not aranan: 
        return render_template('index.html')
    
    # Supabase'ten verileri çek
    response = supabase.table("ilaclar").select("*").execute()
    ilaclar_listesi = response.data
    
    # İlaç nesnelerini ve isimlerini eşleştirelim ki adet bilgisini de alabilelim
    bulunan_ilac = next((i for i in ilaclar_listesi if aranan.lower() in i.get('ilac_adi', '').lower()), None)
    
    ilac_isimleri = [i.get('ilac_adi') for i in ilaclar_listesi if i.get('ilac_adi')]
    
    if bulunan_ilac:
        ilac_adi = bulunan_ilac.get('ilac_adi')
        adet = bulunan_ilac.get('adet', 0)
        return render_template('index.html', sonuc=ilac_adi, durum=True, adet=adet)
    
    # Hata Toleranslı Öneri
    yakin_esyalar = get_close_matches(aranan, ilac_isimleri, n=1, cutoff=0.4)
    if yakin_esyalar:
        onerilen_kayit = next((i for i in ilaclar_listesi if i.get('ilac_adi') == yakin_esyalar[0]), {})
        adet = onerilen_kayit.get('adet', 0)
        return render_template('index.html', sonuc=f"'{aranan}' bulunamadı.", onerilen=yakin_esyalar[0], adet=adet)
    
    return render_template('index.html', sonuc="Bulunamadı", durum=False, adet=0)

# Stok Güncelleme Rotası
@app.route('/stok_guncelle', methods=['POST'])
def stok_guncelle():
    ilac_adi = request.form.get('ilac_adi')
    yeni_adet = request.form.get('yeni_adet')
    
    if ilac_adi and yeni_adet:
        try:
            # Supabase'te ilgili ilacın adet bilgisini güncelle
            supabase.table("ilaclar").update({"adet": int(yeni_adet)}).eq("ilac_adi", ilac_adi).execute()
        except Exception as e:
            print(f"Stok güncellenirken hata oluştu: {e}")
            
    return redirect(url_for('ana_sayfa'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)