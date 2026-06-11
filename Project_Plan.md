# Antigravity Multi-Agent Orkestrasyon Eklentisi (Plug-in)

## Teknik Tasarım ve Sistem İstemi Dokümanı

Bu belge, Antigravity platformu üzerinde çalışacak, izole kotalı, dinamik ve gerçek zamanlı olarak izlenebilir çoklu ajan (multi-agent) mimarisinin teknik tasarım özelliklerini ve bu yapıyı başlatacak ana sistem istemini (system prompt) içermektedir.

Bu eklentinin ilk görevi, paylaşılan yasal mevzuat ve modül mimarisi dokümanı doğrultusunda **"KVKK İş Süreçlerini Otomize Eden SaaS Uygulaması"** projesini otonom olarak inşa etmektir.

---

## 1. Mimari Yapı ve Hiyerarşi (Master-Worker Modeli)

Sistem, Antigravity platformunun kendi yeteneklerini aşırı yüklemeden (overload) ve ana platform kotasını tüketmeden çalışacak şekilde üç katmanlı bir hiyerarşiyle tasarlanmıştır.

```
[Antigravity Aktif Modeli] (Gemini / Claude / OpenCode Terminali)
         │
         ▼ (Function Calling / Tool Execution - Üst Düzey Emirler)
[Python Koordinatör Ajanı] (Silinemez / Durdurulamaz Çekirdek Süreç)
         │
         ├─► [Avukat Ajanlar (x2)] ──────► (Ayarlardan atanan Özel LLM)
         ├─► [Expert Yazılımcılar (x3)] ──► (Ayarlardan atanan Özel LLM)
         ├─► [Frontend Designer (x1)] ──► (Ayarlardan atanan Özel LLM)
         ├─► [Code Reviewer (x1)] ───────► (Ayarlardan atanan Özel LLM)
         └─► [Application Tester (x1)] ──► (Ayarlardan atanan Özel LLM)

```

### Katman 1: Antigravity Master Brain (Stratejist)

* Antigravity içerisinde o an aktif olan model (Gemini, Claude eklentisi veya OpenCode terminal modeli) sistemin **Yüksek Seviyeli Stratejisti** olarak davranır.
* Süreçlerin kod mimarisini doğrudan yazmak yerine, alt katmandaki Python Koordinatörünü bir **Fonksiyon/Araç (Tool)** gibi çağırarak süreci yönetir.

### Katman 2: Python Koordinatör Ajanı (Orkestratör)

* Eklentinin backend çekirdeğinde asenkron (`asyncio`) çalışan, **silinemez ve devre dışı bırakılamaz** statik bir Python sürecidir.
* Master Brain’den gelen üst düzey emirleri alır, bunları mikro görevlere böler, işçi ajanların kuyruğuna (Task Queue) dağıtır ve tüm durum yönetimini koordine eder.

### Katman 3: Paralel İşçi Ajanlar (İş Gücü)

Toplam 8 ajan asenkron bir döngüde paralel olarak çalışır:

* 
**Avukat Ajanlar (x2):** Yasal mevzuat, standart sözleşmeler ve uyumluluk kriterlerini analiz eder.


* 
**Expert Yazılımcılar (x3):** Belirlenen teknoloji yığını ile backend, API ve veri tabanı katmanlarını kodlar.


* 
**Frontend Designer (x1):** Kullanıcı deneyimini ve yasal arayüz gereksinimlerini (çerez banner eşit görünürlüğü vb.) Next.js ile geliştirir.


* 
**Code Reviewer (x1):** Kod kalitesini, güvenlik açıklarını ve veri izolasyon kurallarını (PostgreSQL RLS vb.) denetler.


* 
**Application Tester (x1):** Entegrasyonları, 72 saatlik ihlal SLA alarmlarını ve işlevsel test senaryolarını simüle eder.



---

## 2. Kota İzolasyonu ve Dinamik YZ Sağlayıcı Yönetimi

Eklentinin en kritik maliyet optimizasyonu, işçi ajanların Antigravity ana modelinin kotasını kullanmamasıdır.

* **Bağımsız API Yönetimi:** Eklenti ayarlar panelinden sisteme girilen YZ sağlayıcıları (OpenRouter, Gemini API, OpenAI, Anthropic vb.) ve API anahtarları veri tabanında güvenli bir şekilde saklanır.
* **Dinamik Model Atama:** Her ajanın profil kartına çalışma esnasında (runtime) farklı bir LLM sağlayıcısı atanabilir.
* **Rol ve Havuz Yönetimi:** Kullanıcı arayüz üzerinden koordinatör hariç herhangi bir ajanı silebilir, yeni bir ajan ekleyebilir veya bir ajanın rolünü (örn: Yazılımcı'dan Reviewer'a) anlık olarak değiştirebilir. Rol değiştiğinde Python Koordinatörü ajanın sistem talimatı şablonunu dinamik olarak günceller.

---

## 3. Canlı İzleme ve Duraklatma (Pause/Resume) Mekanizması

* **Anlık İzleme (Modal Panel):** Arayüzde listelenen ajan kartlarının üzerine tıklandığında bir detay modalı açılır. Bu modal, Python backend'indeki asenkron süreçten beslenen bir **WebSocket Stream** hattı açar. Kullanıcı, ajanın o an tam olarak hangi satırı yazdığını, arka planda döndürdüğü "Düşünce Zincirini (Chain of Thought)" ve LLM loglarını canlı olarak görebilir.
* **Müdahale ve Durdurma:** Her işçi ajan bir `asyncio.Event` bayrağı ile kontrol edilir. Arayüzden bir ajan durdurulduğunda event askıya alınır (`.clear()`). Ajan o anki durumunu dondurur ve Antigravity ana modeline veya diğer paralel süreçlere zarar vermeden "Bekleme" moduna geçer. "Devam Et" denildiğinde kaldığı state verisinden çalışmaya devam eder.

---

## 4. Antigravity Master Brain İçin Sistem İstemi (System Prompt)

Antigravity içerisindeki ana modelinizi (Gemini, Claude veya OpenCode) bu eklentiyi yöneten bir **"Stratejist"** haline getirmek için aşağıdaki sistemi başlatma istemini kullanmalısınız:

```text
PROMPT NAME: Antigravity Multi-Agent Orchestrator Master Brain
VERSION: 1.0 (June 2026)
AUTHOR: Antigravity Core

[SİSTEM TALİMATI]
Sen Antigravity platformunun en üst düzey multi-agent stratejistisin (Master Brain). Görevin, sana entegre edilmiş olan ve arka planda çalışan "Python Koordinatör Ajanı" (Core Engine) aracılığıyla 8 adet paralel işçi ajanı yöneterek yazılım projelerini uçtan uca inşa etmektir. 

Şu anki birincil hedefin: üzerinde çalışılan projenin, sana verilen mevzuat haritasına ve fazlı mimari dokümanlarına sadık kalarak tamamlamaktır (varsa dökümanları kullan).

[ÇALIŞMA PRENSİPLERİ VE KOTA KORUMASI]
1. Sen üst düzey görev tanımları, mimari kurallar ve yasal validasyon sınırları belirlersin. Kod yazma, test etme ve yasal analiz işlerini alt işçi ajanlara delege edersin.
2. İşçi ajanları tetiklemek için sana sunulan `manage_worker_agent` fonksiyonunu (Tool) kullanmalısın.
3. İşçi ajanların yapacağı alt LLM çağrıları kendi izole API anahtarları üzerinden yürütülür, senin kotanı tüketmez. Bu yüzden işleri en ince detayına kadar bölüp ajanlara dağıtmaktan çekinme.
4. Python Koordinatör Ajanı senin ana yönetim arayüzündür. Onu disable edemez veya silemezsin. Ancak diğer işçi ajanları (dev_1, lawyer_2 vb.) durdurabilir, rolleri arasında geçiş yaptırabilir veya havuzdan çıkarabilirsin.

[PROJE ÖZELİNDEKİ GÖREV DAĞILIM STRATEJİN]
Süreci dokümanlardaki fazlara göre yönet, örneğin:
- FAZ 1 emirlerini verirken: Üç yazılımcı ajana (dev_1, dev_2, dev_3) PostgreSQL Row-Level Security (RLS) mimarisini kurdur ve Code Reviewer ajana veri izolasyonunu denetlet.
- FAZ 2 emirlerini verirken: Avukat ajanlardan VERBİS kayıt parametrelerini ve hukuki sebepleri (açık rıza, sözleşme, meşru menfaat vb.) netleştirmelerini iste; yazılımcılara bu kurallara göre Excel/API export yapısını kodlat.
- FAZ 3 emirlerini verirken: Frontend designer ajana çerez banner'larında "Tümünü Reddet" ve "Tümünü Kabul Et" butonlarını yasal olarak eşit görünürlükte tasarlat. Tester ajana 30 günlük ilgili kişi başvuru süre alarmlarını test ettir.
- FAZ 4 ve 5 emirlerini verirken: TÜBİTAK Zaman Damgası API entegrasyonu, KEP Gateway ve 72 saatlik ihlal prosedür loglarının değiştirilemezliğini denetlet.

[FONKSİYON ÇAĞRI (TOOL) ŞABLONU]
Bir ajana iş emri göndermek veya durumunu değiştirmek istediğinde sadece şu fonksiyon yapısını tetikle:
manage_worker_agent(agent_id="dev_1", action="START", task_description="Faz 1 kapsamında multi-tenant veri tabanı şeması için PostgreSQL RLS kodlarını ve audit log tablosunu oluştur.")

Ajanların durumunu anlık olarak arayüzdeki WebSocket akışından izle. Bir ajan yasal veya teknik bir hata yaptığında `action="PAUSE"` komutu ile onu durdur, yönlendirmeni yap ve ardından `action="RESUME"` ile süreci devam ettir.


