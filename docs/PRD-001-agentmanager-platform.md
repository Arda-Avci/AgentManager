# PRD-001: AgentManager — Çoklu Ajan Orkestrasyon Platformu

> [📖 English version →](#english-version)

---

## 🇹🇷 Türkçe

### Problem

Günümüzde yazılım geliştiriciler, farklı görevler için birden çok AI ajanı kullanmak istiyor: bir ajan kod yazarken, başka bir ajan dokümantasyon hazırlıyor, üçüncü bir ajan test senaryoları üretiyor. Ancak mevcut çözümler:

- **Platforma kilitli** — Sadece VS Code, sadece CLI veya sadece web arayüzü. Geliştirici iş akışının her noktasında ajanlara erişemiyor.
- **Tek model bağımlısı** — agentclaw gibi çözümler yalnızca Claude çalıştırabiliyor. Oysa her görev için farklı model (hızlı/ucuz vs güçlü/pahalı) kullanmak maliyet optimizasyonu için kritik.
- **Mantık tek bir prompt dosyasında** — Tüm ajan mantığı CLAUDE.md/SOUL.md gibi tek bir dosyada, test edilemez, versiyonlanamaz, ölçeklenemez.
- **Platform entegrasyonu yok** — Agent'lar IDE'ye, terminale veya Telegram'a native olarak bağlanamıyor.

AgentManager, bu sorunları çözmek için geliştiricinin tüm çalışma alanında (IDE + terminal + messaging) çalışan, çok modelli, modüler bir ajan orkestrasyon platformudur.

### Çözüm

AgentManager, üç ana prensip üzerine kurulu bir platformdur:

1. **Her yerde çalışır** — VS Code extension, Antigravity plugin, Codex CLI, Cursor, Windsurf ve Telegram bot olarak. Tüm platformlar MCP (Model Context Protocol) ile merkezi Python Core'a bağlanır.
2. **Her modeli çalıştırır** — OpenAI, Claude, Gemini, Ollama (yerel), OpenRouter. Her ajan bağımsız model ataması yapabilir, hata durumunda fallback zinciri çalışır.
3. **Modüler ve test edilebilir** — Her ajan bir Python class'ı, her provider bir modül, her platform bir plugin. VCR record/replay ile provider bağımlılığı olmadan test edilebilir.

Kullanıcı `pip install agentmanager-core` ile Core'u kurar, `npm install -g agentmanager-plugins` ile plugin'leri ekler, Telegram'da `/agent create code-agent` ile yeni bir ajan oluşturur.

### Kullanıcı Hikayeleri

1. Bir geliştirici olarak, terminalden AI ajanı oluşturabilmek istiyorum (`agentmanager agent create`), böylece görevleri terminalden ayrılmadan otomatikleştirebileyim.
2. Bir geliştirici olarak, her ajanın farklı bir LLM modeli kullanmasını istiyorum (örn. code-agent Claude 4, test-agent GPT-4o, research-agent Gemini kullanır), böylece maliyet ve yetenek optimizasyonu yapabileyim.
3. Bir geliştirici olarak, Telegram üzerinden ajanlarımla konuşmak istiyorum, böylece masamda olmasam da görev atayabileyim.
4. Bir geliştirici olarak, tüm ajanlarımı VS Code yan panelinde görüp yönetmek istiyorum, böylece durum, log ve metrikleri izleyebileyim.
5. Bir geliştirici olarak, ajanlarımın kısa dönem (konuşma geçmişi) ve uzun dönem (kalıcı bilgi) belleğe sahip olmasını istiyorum.
6. Bir geliştirici olarak, ana model rate-limit veya hata verdiğinde ajanın otomatik daha ucuz/hızlı modele geçmesini istiyorum.
7. Bir geliştirici olarak, ajanları cron zamanlamasıyla çalıştırmak istiyorum (örn. "her sabah 9'da daily-standup ajanı çalışsın").
8. Bir geliştirici olarak, ajanlara özel araçlar atamak istiyorum (web search, file I/O, GitHub API, Jira), böylece mevcut araç zincirimle etkileşime geçsin.
9. Bir geliştirici olarak, ajanların birbirine görev devredebilmesini istiyorum (örn. code-agent test-agent'dan test yazmasını ister), böylece karmaşık iş akışları otomatik koordine edilsin.
10. Bir geliştirici olarak, ajanlarımın yaptıklarını gerçek zamanlı izlemek istiyorum (WebSocket → React panel), böylece hata ayıklama yapabileyim.
11. Bir geliştirici olarak, ajan şablonları tanımlamak istiyorum (örn. "code-reviewer", "doc-writer"), böylece hızlıca uzmanlaşmış ajanlar kurabileyim.
12. Bir geliştirici olarak, ajanların MCP protokolünde çalışmasını istiyorum, böylece MCP uyumlu her platform (Claude Desktop, gelecek IDE'ler) onları kontrol edebilsin.
13. Bir geliştirici olarak, her ajanın verisinin diğerlerinden izole olmasını istiyorum.
14. Bir geliştirici olarak, cihazlarımı API anahtarlarıyla doğrulamak istiyorum, böylece sadece yetkili istemciler Core'a erişebilsin.
15. Bir geliştirici olarak, sistemin %100 yerel çalışmasını istiyorum (Ollama + local SQLite), böylece verilerimi üçüncü tarafa göndermek zorunda kalmayayım.

### Uygulama Kararları

#### Mimari: Hibrit Stack

| Katman | Teknoloji | Amaç |
|--------|-----------|------|
| Core Orkestrasyon | **Python (FastAPI + SQLAlchemy 2.0 async)** | LLM routing, ajan yaşam döngüsü, state yönetimi, MCP server |
| Platform Pluginler | **TypeScript** | VS Code ext, Antigravity, Codex CLI, Cursor, Windsurf entegrasyonları |
| Web Panel | **React (Vite + Tailwind)** | Ajan dashboard, gerçek zamanlı loglar, yapılandırma UI'ı |
| Veritabanı | **SQLAlchemy 2.0 + Alembic ile SQLite** | Ajan konfigları, oturumlar, loglar, cron kayıtları |
| Protokol | **MCP (Model Context Protocol) HTTP/SSE üzerinden** | Tüm katmanlar arası iletişim |

#### Modül Yapısı

**agentmanager-core/**
- `core/` — FastAPI uygulaması, MCP server kurulumu, middleware
- `agents/` — BaseAgent abstract class + ajan yaşam döngüsü (create, start, stop, delete)
- `providers/` — LLM provider arayüzü + implementasyonlar (OpenAI, Claude, Gemini, Ollama, OpenRouter)
- `router.py` — LLM Router: statik konfig + ajan başına fallback zinciri
- `session.py` — Oturum yöneticisi: chat_id → active_agent eşlemesi
- `cron.py` — Plugin-seviye cron kayıt API'si + heartbeat denetleyicisi
- `database/` — SQLAlchemy modelleri, Alembic migrasyonları, repository katmanı
- `models/` — API kontratları için Pydantic şemaları
- `auth/` — API anahtarı + cihaz eşleme, ajan-seviye veri bölümleme

**agentmanager-providers/**
- `providers/openai/` — OpenAI provider modülü
- `providers/claude/` — Anthropic Claude provider modülü
- `providers/gemini/` — Google Gemini provider modülü
- `providers/ollama/` — Ollama yerel provider modülü
- `providers/mock/` — Test için mock provider (VCR record/replay)

**agentmanager-plugins/**
- `plugins/mcp-client/` — Paylaşımlı MCP istemci kütüphanesi
- `plugins/vscode/` — VS Code eklentisi (webview panel + durum çubuğu)
- `plugins/antigravity/` — Antigravity plugin entegrasyonu
- `plugins/codex-cli/` — Codex CLI entegrasyonu
- `plugins/cursor/` — Cursor editör plugin'i
- `plugins/windsurf/` — Windsurf editör plugin'i

**agentmanager-panel/**
- `src/` — React uygulaması
  - Dashboard — ajan durumu, metrikler, sağlık
  - Agent CRUD — tam konfig ile ajan oluştur/düzenle/sil
  - Log Stream — WebSocket ile gerçek zamanlı ajan logları
  - Settings — global konfig, API anahtarları, provider kimlik bilgileri

**agentmanager-bot/**
- `bot/` — Telegram botu (tek bot, çoklu ajan yönlendirme)
- `handlers/` — Komut yöneticileri (/agent, /task, /list, /cron)
- `sessions/` — Sohbet oturumu state yönetimi
- `keyboards/` — Ajan seçimi için inline klavyeler

**agentmanager-scheduler/**
- `registry/` — Cron iş kaydı (plugin-seviye, Core API ile persist)
- `heartbeat/` — Core heartbeat ile kaçırılan tetikleme tespiti
- `executors/` — Cron iş yürütücüleri

**agentmanager-auth/**
- `keys/` — API anahtarı oluşturma, doğrulama, döndürme
- `pairing/` — Cihaz eşleme akışı
- `partition/` — Ajan-seviye veri izolasyon middleware'i

**agentmanager-test/**
- `vcr/` — Provider testleri için record & replay framework'ü
- `fixtures/` — Test fix'leri ve mock veri
- `integration/` — Entegrasyon test paketleri

#### Temel Mimari Kararlar

1. **MCP evrensel protokol** — Tüm pluginler Core ile MCP üzerinden iletişim kurar. Gelecekteki MCP uyumlu platformlar yeni plugin kodu gerektirmez.
2. **Hibrit state** (Core kalıcı, Plugin geçici cache) — Core tek doğruluk kaynağıdır. Pluginler sadece okuma performansı için cache tutar.
3. **Statik konfig + ajan başına fallback zinciri** — Her ajan birincil provider/model ve sıralı fallback listesi tanımlar.
4. **Sliding window + özetleme** — Context window N mesajla sınırlanır; eski mesajlar özetlenip system prompt'una enjekte edilir.
5. **Chat-tabanlı oturum yönlendirme** — Her `chat_id` SQLite'da bir `active_agent`'e eşlenir.
6. **Plugin-seviye cron, Core heartbeat güvenlik ağı** — Cron plugin katmanında yaşar; Core periyodik olarak kaçırılan tetiklemeleri kontrol eder.
7. **API anahtarı + cihaz eşleme** — Hafif auth. OAuth bağımlılığı yok.
8. **Ajan-seviye veri bölümleme** — Her sorgu `agent_id` ile kapsamlanır. Middleware API katmanında zorunlu kılar.

### Test Kararları

- **Dış davranışı test et**, implementasyon detaylarını değil.
- İyi test: ajan oluştur → mesaj gönder → yanıtın beklenen pattern'le eşleştiğini doğrula.
- Provider testleri için **VCR (record & replay)** kullan. Gerçek API yanıtları bir kez kaydedilir, CI'da replay edilir.
- Tüm Core API'leri mock provider ile entegrasyon testine sahip olmalı.

### Kapsam Dışı

- GUI tabanlı ajan oluşturucu (sürükle-bırak) — gelecek sürüm
- Çok kullanıcılı/çok kiracılı SaaS — v2
- Fine-tuning API'si — AgentManager modelleri eğitmez, orkestre eder
- Vector DB (RAG) — sliding window + özetleme v1 için yeterli, v2'de değerlendirilecek
- İOS/Android mobil uygulama — Telegram bot mobil arayüz, native uygulamalar v2
- Plugin pazar yeri — v1 sonrası
- Kurumsal SSO (LDAP, SAML) — v2
- Sesli ajan (TTS/STT) — v2

### Ek Notlar

- **Geliştirme Fazlaması:** Faz 0 (Foundation: Python Core) önce tamamlanır. Sonra 5 paralel track: 1A (MCP+Panel), 1B (Telegram), 1C (Provider'lar), 1D (Auth+Cron+Memory), 2C (MCP Client).
- **GitHub:** [https://github.com/Arda-Avci/AgentManager](https://github.com/Arda-Avci/AgentManager)
- **Referans Projeler:** lobe-chat (multi-provider UI), my-SuperAGI (tool system), Auto-GPT (chain-of-thought), aider (git integration), AgentGPT (task loop). Detay: `orkun.md`.
- **Dil:** Kodda İngilizce, dokümantasyonda Türkçe (AGENTS.md gereği).

---

<h1 id="english-version"></h1>

## 🇬🇧 English Version

### Problem Statement

Modern developers need multiple AI agents for different tasks: one writes code, another prepares documentation, a third generates tests. Current solutions fail because:

- **Platform-locked** — Only VS Code, only CLI, or only web. No cross-platform access.
- **Single-model dependency** — agentclaw only runs Claude. Different tasks need different models (fast/cheap vs powerful/expensive).
- **Logic in a single prompt file** — All agent logic in CLAUDE.md/SOUL.md, untestable, unversioned, unscalable.
- **No platform integration** — Agents can't natively connect to IDE, terminal, or Telegram.

AgentManager is a multi-model, modular agent orchestration platform that works across the developer's entire workspace (IDE + terminal + messaging).

### Solution

Three core principles:

1. **Runs everywhere** — VS Code extension, Antigravity plugin, Codex CLI, Cursor, Windsurf, Telegram bot. All platforms connect to the Python Core via MCP.
2. **Runs every model** — OpenAI, Claude, Gemini, Ollama (local), OpenRouter. Per-agent independent model assignment with fallback chains.
3. **Modular and testable** — Each agent is a Python class, each provider is a module, each platform is a plugin. VCR record/replay enables testing without provider dependencies.

### User Stories

1. As a developer, I want to create an AI agent from the command line (`agentmanager agent create`), so that I can automate tasks without leaving the terminal.
2. As a developer, I want each agent to use a different LLM model (e.g., code-agent uses Claude 4, test-agent uses GPT-4o, research-agent uses Gemini), so that I can optimize cost and capability per task.
3. As a developer, I want to talk to my agents via Telegram, so that I can delegate tasks while away from my desk.
4. As a developer, I want to see all my agents in a VS Code sidebar panel, so that I can monitor status, logs, and metrics without switching context.
5. As a developer, I want agents to have short-term (conversation) and long-term (persistent) memory.
6. As a developer, I want fallback to cheaper/faster models on rate-limit or error.
7. As a developer, I want cron-scheduled agent execution (e.g., "daily standup every 9 AM").
8. As a developer, I want custom tools per agent (web search, file I/O, GitHub API, Jira).
9. As a developer, I want agents to delegate tasks to each other (code-agent → test-agent).
10. As a developer, I want real-time streaming logs via WebSocket to the React panel.
11. As a developer, I want agent templates ("code-reviewer", "doc-writer") for quick setup.
12. As a developer, I want agents to run on MCP protocol for any MCP-compatible platform.
13. As a developer, I want per-agent data isolation.
14. As a developer, I want API key authentication for authorized client access.
15. As a developer, I want 100% local operation (Ollama + local SQLite).

### Implementation Decisions

Same architecture, module breakdown, and key decisions as the Turkish version above.

### Testing Decisions

- Test **external behavior**, not implementation details.
- Use **VCR (record & replay)** for provider tests — record once, replay in CI.
- All Core APIs must have integration tests with mock providers.

### Out of Scope

- GUI-based agent builder (drag & drop) — future version
- Multi-tenant SaaS — v2
- Fine-tuning API
- Vector DB for RAG — v2
- Native mobile apps — v2
- Plugin marketplace — post-v1
- Enterprise SSO — v2
- TTS/STT — v2

### Further Notes

- **Phasing:** Phase 0 (Foundation: Python Core) first. Then 5 parallel tracks: 1A (MCP+Panel), 1B (Telegram), 1C (Providers), 1D (Auth+Cron+Memory), 2C (MCP Client).
- **Repo:** [https://github.com/Arda-Avci/AgentManager](https://github.com/Arda-Avci/AgentManager)
- **References:** lobe-chat, my-SuperAGI, Auto-GPT, aider, AgentGPT. Details in `orkun.md`.
