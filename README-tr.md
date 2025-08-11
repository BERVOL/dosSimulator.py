# DoS Simulator

Bu proje, Dağıtılmış Hizmet Engelleme (DoS) saldırılarının simülasyonunu gerçekleştiren bir araçtır. Ağ güvenliği alanında eğitim ve test amaçlı kullanılabilir.

## Özellikler

- Belirli bir hedef IP ve port'a çok sayıda istek göndererek DoS saldırısı simülasyonu yapar.
- TCP, UDP ve HTTP protokollerini destekler.
- Saldırı yoğunluğunu ve süresini ayarlayabilme.
- Çoklu iş parçacığı (multithreading) ile yüksek performans.
- Basit ve kullanıcı dostu komut satırı arayüzü.

## Gereksinimler

- Python 3.6 ve üzeri
- Gerekli Python kütüphaneleri: `requests` (HTTP saldırıları için)
  
Kurulum için:

```bash
pip install -r requirements.txt
```

## Kullanım

Terminal veya komut satırından aşağıdaki şekilde çalıştırabilirsiniz:

```bash
python dos_simulator.py --target 192.168.1.10 --port 80 --protocol tcp --threads 100 --duration 60
```

Parametreler:

- `--target`: Hedef IP adresi veya domain adı.
- `--port`: Hedef port numarası.
- `--protocol`: Kullanılacak protokol (tcp, udp, http).
- `--threads`: Aynı anda çalışacak iş parçacığı sayısı.
- `--duration`: Saldırının süresi (saniye cinsinden).

## Örnek

```bash
python dos_simulator.py --target example.com --port 80 --protocol http --threads 50 --duration 120
```

Bu komut, `example.com` adresine HTTP protokolü kullanarak 50 iş parçacığı ile 120 saniye boyunca saldırı yapar.

## Uyarılar

- Bu araç sadece eğitim ve test amaçlı kullanılmalıdır.
- İzinsiz saldırılar yasa dışıdır ve ciddi hukuki sonuçları olabilir.
- Kendi ağınızda veya izin verilen ortamda kullanınız.

## İleri Seviye Kullanım

- Kaynak IP adresini rastgele değiştirme (IP spoofing) özelliği eklenebilir.
- Saldırı türleri (SYN flood, UDP flood, HTTP GET flood vb.) genişletilebilir.
- Grafiksel arayüz eklenerek kullanım kolaylaştırılabilir.


