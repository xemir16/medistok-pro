while True: 
    print("\n--- STOK TAKİP MENÜSÜ ---")
    print("1 - Ürün ekle")
    print("2 - Ürünleri listele")
    print("3 - Stok güncelle")
    print("4 - Çıkış")

    secim = input("Seçiminizi giriniz: ")

    if secim == "1":
        print("Ürün ekleme seçildi")

    elif secim == "2":
        print("Ürün listeleme seçildi")
    
    elif secim == "3":
        print("Stok güncelleme seçildi")

    elif secim == "4":
        print("Programdan Çıkış yapılıyor...")
        break

    else:
        print("Geçersiz seçim tekrar deneyiniz")


