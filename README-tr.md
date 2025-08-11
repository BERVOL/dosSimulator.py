# DoS Simulator

Bu proje, Dağıtılmış Hizmet Engelleme (DoS) saldırılarının simülasyonunu gerçekleştiren, özellikle HTTP protokolü üzerinde çalışan bir araçtır. Ağ güvenliği alanında eğitim ve test amaçlı kullanılabilir.

## Özellikler

- Hedef web sunucusuna HTTP istekleri göndererek DoS saldırısı simülasyonu yapar.
- Asenkron (async) yöntemlerle yüksek performans sağlar.
- Canlı istatistikler ile saldırı süresince performans takibi yapılabilir.
- Detaylı loglama ve raporlama özellikleri mevcuttur.
- Basit ve kullanıcı dostu etkileşimli terminal arayüzü.

## Gereksinimler

- Python 3.6 ve üzeri
- Gerekli Python kütüphaneleri: `requests`, `aiohttp` (HTTP saldırıları için asenkron istekler)
  
Kurulum için:

```bash
pip install -r requirements.txt
```

## Kullanım

Aracı terminal veya komut satırından çalıştırdığınızda, hedef URL, saldırı süresi ve istek yoğunluğu gibi parametreleri etkileşimli olarak girmeniz istenir. Bu sayede kullanıcı dostu ve kolay bir kullanım deneyimi sağlar.

Örneğin, program çalıştırıldığında aşağıdaki gibi sorularla karşılaşırsınız:

- Hedef URL'yi giriniz: 
- Saldırı süresi (saniye): 
- Eş zamanlı istek sayısı: 

Bu bilgileri girdikten sonra saldırı başlar ve canlı istatistikler ile saldırının durumu takip edilebilir.

## Uyarılar

- Bu araç sadece eğitim ve test amaçlı kullanılmalıdır.
- İzinsiz saldırılar yasa dışıdır ve ciddi hukuki sonuçları olabilir.
- Kendi ağınızda veya izin verilen ortamda kullanınız.

## İleri Seviye Kullanım

- Kaynak IP adresini rastgele değiştirme (IP spoofing) özelliği eklenebilir.
- Saldırı türleri (HTTP GET flood, POST flood vb.) genişletilebilir.
- Grafiksel arayüz eklenerek kullanım kolaylaştırılabilir.
