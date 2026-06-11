# Orkun İşitmak — Repo Analizi

**Tarih:** 2026-06-11
**Kaynak:** https://github.com/orkunisitmak?tab=repositories
**Amaç:** AgentManager projesine entegre edilebilecek özelliklerin tespiti

---

## 1. lobe-chat

**Repo:** https://github.com/orkunisitmak/lobe-chat
**Orijinal:** lobehub/lobe-chat
**Yıldız:** ~35k+
**Dil:** TypeScript

### Ne işe yarar?
Açık kaynak, modern tasarımlı bir LLM/AI chat framework'ü. OpenAI, Claude 3, Gemini, Ollama, Bedrock, Azure, Mistral, Perplexity gibi **20+ sağlayıcıyı** tek arayüzde toplar. Plugin sistemi, görsel tanıma, TTS/STT, görsel üretim (DALL-E, MidJourney) destekler. Tek tıkla Vercel/Docker deploy edilebilir.

### AgentManager'a entegre edilebilecek özellikler

| # | Özellik | Açıklama |
|---|---------|----------|
| 1.1 | **Multi-Provider Yönetimi** | 20+ LLM sağlayıcısını tek bir arayüzde toplama pattern'i. AgentManager'ın LLM Router'ı için referans implementasyon. |
| 1.2 | **Plugin Sistemi (Function Calling)** | LobeChat'in plugin ekosistemi — harici araçların AI'a yetenek olarak eklenmesi. AgentManager'ın MCP Client + tool sistemi için birebir. |
| 1.3 | **Agent Market / GPTs** | Kullanıcıların kendi ajanlarını oluşturup paylaştığı market. AgentManager'ın rol/şablon sistemi için ilham. |
| 1.4 | **Ollama Entegrasyonu** | Yerel modellerin LobeChat'e bağlanma şekli. AgentManager'ın Ollama provider'ı için referans. |
| 1.5 | **Session Yönetimi** | Çoklu oturum, mesaj geçmişi, context window yönetimi. AgentManager'ın memory sistemi için. |
| 1.6 | **TTS/STT** | Sesli girdi/çıktı. AgentManager'ın bot kanallarına sesli mesaj desteği eklemek için. |
| 1.7 | **Tema ve UI Bileşenleri** | Modern React UI, mobile uyum, PWA. AgentManager'ın Web Panel'i için referans tasarım. |

---

## 2. my-SuperAGI

**Repo:** https://github.com/orkunisitmak/my-SuperAGI
**Orijinal:** TransformerOptimus/SuperAGI
**Yıldız:** ~15k+
**Dil:** Python (%62), JavaScript (%29)

### Ne işe yarar?
Geliştirici odaklı, açık kaynak otonom AI ajan framework'ü. Ajan oluşturma, yönetme, çalıştırma. Araç desteği (Slack, Email, Jira, GitHub, Zapier, Discord, Google Search, DALL-E), eşzamanlı ajan çalıştırma, GUI, vector DB bellek, token optimizasyonu.

### AgentManager'a entegre edilebilecek özellikler

| # | Özellik | Açıklama |
|---|---------|----------|
| 2.1 | **Tool/Araç Sistemi** | Slack, Email, Jira, GitHub, Zapier, Google Search, Discord gibi harici araçlar. AgentManager'ın ajan yetenekleri için referans. |
| 2.2 | **Concurrent Agent Yönetimi** | Birden çok ajanı eşzamanlı çalıştırma altyapısı. AgentManager'ın Worker Pool'u için. |
| 2.3 | **Vector DB Bellek** | Pinecone vb. vector DB ile uzun süreli bellek. AgentManager'ın per-agent memory store'u için. |
| 2.4 | **Agent Trajectory Fine-Tuning** | Ajanın karar zincirini kaydetme ve iyileştirme. AgentManager'ın chain-of-thought log sistemi için. |
| 2.5 | **Looping Detection** | Sonsuz döngü tespiti ve heuristics. AgentManager'ın hata yönetimi için. |
| 2.6 | **Resource Manager** | Token kullanımı, maliyet takibi. AgentManager'ın kota yönetimi için birebir. |
| 2.7 | **GUI Dashboard** | Ajan yönetim arayüzü. AgentManager'ın Web Panel'i için referans. |
| 2.8 | **Action Console** | Ajan eylemlerini canlı izleme konsolu. AgentManager'ın WebSocket canlı log akışı için. |

---

## 3. AgentGPT

**Repo:** https://github.com/orkunisitmak/AgentGPT
**Orijinal:** reworkd/AgentGPT
**Yıldız:** ~30k+
**Dil:** TypeScript (%93)

### Ne işe yarar?
Browser üzerinden otonom AI ajanları oluşturma, yapılandırma ve deploy etme. Kullanıcı kendi AI'sına bir hedef verir, AI bu hedefe ulaşmak için görevler düşünür, uygular ve sonuçlardan öğrenir. Next.js + Prisma + Supabase stack.

### AgentManager'a entegre edilebilecek özellikler

| # | Özellik | Açıklama |
|---|---------|----------|
| 3.1 | **Hedef-Tabanlı Görev Döngüsü** | "Hedef belirle → görev üret → uygula → öğren → tekrar" döngüsü. AgentManager'ın task queue mantığı için. |
| 3.2 | **Browser İçi Ajan Deploy** | Kullanıcının browser'dan ajan oluşturup çalıştırması. AgentManager'ın VS Code Webview + Web Panel UX'i için. |
| 3.3 | **Prisma ORM Kullanımı** | SQLite/PostgreSQL yönetimi. AgentManager'ın state store katmanı için referans. |
| 3.4 | **tRPC Type-safe API** | End-to-end typesafe API pattern'i. AgentManager'ın TS katmanındaki API tasarımı için. |

---

## 4. Auto-GPT

**Repo:** https://github.com/orkunisitmak/Auto-GPT
**Orijinal:** Significant-Gravitas/AutoGPT
**Yıldız:** ~165k+
**Dil:** Python (%99)

### Ne işe yarar?
GPT-4'ün tamamen otonom çalışmasını sağlayan deneysel proje. İnternet erişimi, uzun/kısa vadeli bellek yönetimi, dosya depolama, Google arama, web etkileşimi. Auto-GPT, LLM "düşüncelerini" zincirleyerek belirlediğiniz hedefe otonom ulaşır.

### AgentManager'a entegre edilebilecek özellikler

| # | Özellik | Açıklama |
|---|---------|----------|
| 4.1 | **Otonom Düşünce Zinciri (Chain-of-Thought)** | LLM'in adım adım düşünmesi, plan yapması, uygulaması. AgentManager'ın chain-of-thought log sistemi için referans. |
| 4.2 | **Çoklu Bellek Backend** | Local JSON, Redis, Pinecone arasında geçiş. AgentManager'ın state store esnekliği için. |
| 4.3 | **İnternet Erişimi** | Google arama, web scraping. AgentManager'ın MCP Client + web tool yeteneği için. |
| 4.4 | **Dosya Yönetimi** | Çıktıları kaydetme, özetleme. AgentManager'ın görev çıktı yönetimi için. |
| 4.5 | **Continuous Mode** | Kullanıcı onayı olmadan otomatik çalışma. AgentManager'ın tam otonom modu için. |
| 4.6 | **CLI Argüman Yönetimi** | Zengin CLI parametreleri (`--speak`, `--continuous`, `--gpt3only`). AgentManager'ın CLI tasarımı için. |

---

## 5. aider

**Repo:** https://github.com/orkunisitmak/aider
**Orijinal:** Aider-AI/aider
**Yıldız:** ~20k+
**Dil:** Python (%97)

### Ne işe yarar?
Terminalde çalışan, GPT ile kod yazma/düzenleme aracı. Git entegrasyonu, otomatik commit, diff/undo, çoklu dosya düzenleme, ctags ile repo haritası çıkarma.

### AgentManager'a entegre edilebilecek özellikler

| # | Özellik | Açıklama |
|---|---------|----------|
| 5.1 | **Git Entegrasyonu** | Otomatik commit, diff görüntüleme, undo. AgentManager'ın kod üreten ajanları için. |
| 5.2 | **Repo Haritası (ctags)** | Tüm repo yapısını anlama ve büyük kod tabanlarında gezinme. AgentManager'ın developer ajanlarına yetenek olarak. |
| 5.3 | **Çoklu Dosya Düzenleme** | GPT'nin birden çok dosyada koordineli değişiklik yapması. AgentManager'ın task zinciri için. |
| 5.4 | **In-Chain Chat Komutları** | `/add`, `/drop`, `/undo`, `/diff`, `/run` gibi komutlar. AgentManager'ın bot komut dili tasarımı için. |
| 5.5 | **Context Window Yönetimi** | Hangi dosyaların GPT'e gönderileceğini belirleme. AgentManager'ın LLM token optimizasyonu için. |

---

## 6. Diğer Repolar (Düşük Öncelik)

| Repo | Orijinal | Ne İşe Yarar | Alakası |
|------|----------|-------------|---------|
| **ChatGPT-Next-Web** | ChatGPTNextWeb/NextChat | ChatGPT web UI (Vercel deploy) | Düşük — sadece UI pattern'leri |
| **midjourney-proxy** | novicezk/midjourney-proxy | MidJourney API proxy | Düşük — görsel üretim yeteneği olarak eklenebilir |
| **Feishu-OpenAI** | ConnectAI-E/feishu-openai | Feishu × GPT entegrasyonu | Düşük — farklı bir platform (Çin pazarı) |
| **Auto-Synced-Translated-Dubs** | ThioJoe/Auto-Synced-Translated-Dubs | Video dublaj/çeviri | Yok — alakasız |
| **orkai-chatgpt-clone** | danny-avila/LibreChat | ChatGPT clone | Düşük — LibreChat fork'u |
| **stable-diffusion-webui** | Sygil-Dev/sygil-webui | SD web UI | Düşük — görsel üretim |
| **text2img-index** | **ORJİNAL** | Text-to-image araç listesi | Düşük — liste/derleme projesi |
| **instant-ngp** | NVlabs/instant-ngp | Neural graphics primitives (NeRF) | Yok — bilimsel proje |

---

## Özet: En Önemli Entegrasyonlar

| Sıra | Repo | Alınacak Özellik | AgentManager'da Yeri |
|------|------|------------------|---------------------|
| 🥇 | **lobe-chat** | Multi-provider sistemi, plugin ekosistemi, Ollama entegrasyonu | LLM Router, MCP Client, Provider Registry |
| 🥇 | **my-SuperAGI** | Tool sistemi, concurrent agent, vector DB, token takibi | Worker Pool, Memory Store, Kota Yönetimi |
| 🥈 | **Auto-GPT** | Chain-of-thought, çoklu bellek backend, continuous mode | Log Sistemi, State Store, Otonom Mod |
| 🥉 | **aider** | Git entegrasyonu, repo haritası, in-chain komutlar | Developer Ajan Yetenekleri, Bot Komut Dili |
| 🥉 | **AgentGPT** | Hedef-tabanlı görev döngüsü, browser deploy | Task Queue, UX Pattern'leri |

---

## Referans Kod Yapıları (İncelenmeli)

AgentManager geliştirilirken şu dosya/klasör yapılarına bakılması önerilir:

```
lobe-chat/src/              → Provider ekleme pattern'i, plugin sistemi
my-SuperAGI/superagi/       → Tool tanımları, worker yönetimi
Auto-GPT/autogpt/           → Chain-of-thought, memory backends
aider/aider/                → Git integration, diff yönetimi
AgentGPT/src/               → Goal-based task loop, Prisma şeması
```
