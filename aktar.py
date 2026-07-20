import json
from supabase import create_client

# Supabase bilgilerin
URL = "https://haaoborfpaexelqmgmkx.supabase.co"
KEY = "sb_publishable_SFMcmpXgybgVEFBgQApyKQ_39O_Lq3i"

supabase = create_client(URL, KEY)

def json_verilerini_aktar():
    try:
        # ilaclar.json dosyasını oku
        with open('ilaclar.json', 'r', encoding='utf-8') as f:
            veriler = json.load(f)
            
        print(f"JSON dosyasından {len(veriler)} adet ilaç okundu. Supabase'e aktarılıyor...")
        
        # Verileri Supabase'e ekle
        for item in veriler:
            # Veri direkt metin mi yoksa sözlük mü kontrol edelim
            if isinstance(item, dict):
                ilac_adi = item.get('ilac_adi') or item.get('isim') or str(item)
            else:
                ilac_adi = str(item)
            
            try:
                supabase.table("ilaclar").insert({"ilac_adi": ilac_adi}).execute()
                print(f"Eklendi: {ilac_adi}")
            except Exception as e:
                print(f"Zaten var veya hata ({ilac_adi}): {e}")
                
        print("\n Aktarım tamamlandı usta!")
        
    except FileNotFoundError:
        print("Hata: 'ilaclar.json' dosyası bulunamadı!")

if __name__ == "__main__":
    json_verilerini_aktar()