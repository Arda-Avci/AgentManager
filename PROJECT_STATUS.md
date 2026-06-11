# Proje Durumu / Project Status

**Son Güncelleme:** 2026-06-11

---

## Genel Durum / Overall Status

| Alan | Durum | Açıklama |
|------|-------|----------|
| **Tasarım** | ✅ Tamamlandı | Spec dokümanı onaylandı, grill testi geçti |
| **Mimari** | ✅ Belirlendi | Python Core + TypeScript Plugins + React Panel |
| **Dökümantasyon** | ✅ Oluşturuldu | README (TR/EN), yardım dökümanları, orkun.md |
| **Repo Analizi** | ✅ Tamamlandı | 13 repo analiz edildi (orkun.md), pattern'ler belirlendi |
| **PRD** | ✅ Yayımlandı | GitHub Issue #1 |
| **Özellik Planı** | ✅ Güncellendi | 60+ madde, 10 faz, 5 paralel track (TODO.md) |
| **Geliştirme** | ⏳ Başlamadı | Faz 0 bekliyor |

---

## Yapılanlar / Completed

- [x] Proje analizi (agentclaw, appflowy, mevcut plan)
- [x] Tasarım beyin fırtınası ve onay
- [x] Tasarım grill testi (15 soru, tüm kararlar netleşti)
- [x] Spec dokümanı: `docs/2026-06-11-agentmanager-plugin-design.md`
- [x] README.md (Türkçe + İngilizce)
- [x] Yardım dökümanları (`docs/help/`)
  - Kurulum Kılavuzu / Setup Guide
  - Kullanım Kılavuzu / Usage Guide
  - Ajan Yönetimi / Agent Management
  - SSS / FAQ
- [x] AGENTS.md (agent yönergeleri)
- [x] Project_Plan.md (ilk plan dokümanı)
- [x] 13 GitHub repo analizi (orkun.md) — pattern çıkarımı
- [x] PRD Issue #1: https://github.com/Arda-Avci/AgentManager/issues/1

---

## Mimari Kararlar / Architecture Decisions

### ADR-001: Hibrit Teknoloji Yığını
- **Karar:** Python Core + TypeScript Plugins + React Panel
- **Gerekçe:** Python LLM ekosistemi en geniş, TypeScript platform eklentileri için doğal dil, React web panel için esnek
- **Detay:** `docs/2026-06-11-agentmanager-plugin-design.md`

### ADR-002: Ajan Başına Bağımsız Model
- **Karar:** Her ajan farklı bir LLM sağlayıcısı/model kullanabilir
- **Gerekçe:** Maliyet optimizasyonu, göreve özel model seçimi, kota izolasyonu

### ADR-003: Master-Worker Modeli
- **Karar:** Üç katmanlı hiyerarşi (Platform → Python Orkestratör → İşçi Ajanlar)
- **Gerekçe:** Ana platform kotasını koruma, paralel çalışma, izole hata yönetimi

### ADR-004: Tek Telegram Botu
- **Karar:** Tüm ajanları tek bir Telegram botu yönetir (agentclaw'ın her ajan için ayrı bot pattern'inin tersi)
- **Gerekçe:** Merkezi Python Core sayesinde tüm ajanlara tek noktadan erişim, daha basit yönetim
- **Komutlar:** /status, /agent, /tasks, /pause, /resume, /report

### ADR-005: Paralel Faz Yapısı
- **Karar:** Faz 0'dan sonra 5 bağımsız track paralel ilerler (1A MCP+Panel, 1B Telegram, 1C Çoklu Model, 1D Auth+Cron+Memory, 2C MCP Client)
- **Gerekçe:** Bağımsız özelliklerin blokaj olmadan eşzamanlı geliştirilmesi

### ADR-006: Tasarım Kararları (Grill Sonuçları)
- **Karar:** Aşağıdaki 15 karar grill testi sonucu netleştirilmiştir
- **Gerekçe:** Tasarımın tüm kritik dalları test edildi, zayıf noktalar belirlendi

| # | Karar | Seçim |
|---|-------|-------|
| 1 | İletişim Protokolü | **MCP** (Python Core server, TS plugin client) |
| 2 | State Mimarisi | **Hybrid** — Core persistent, Plugin volatile cache |
| 3 | ORM/Database | **SQLAlchemy 2.0 async + Alembic** |
| 4 | LLM Routing | **Hybrid** — statik config + fallback zinciri |
| 5 | Fallback Stratejisi | **Pre-configured fallback chain** (hata tipine göre sıralı) |
| 6 | Worker Pool | **Asyncio task pool** |
| 7 | Bellek Yönetimi | **Sliding window + summarization** |
| 8 | Telegram Session | **Chat-based session routing** (chat_id → active_agent) |
| 9 | Cron Sistemi | **Plugin-level cron** (Core sadece API sağlar) |
| 10 | Cron Resilience | **Core, plugin down olsa da agent'a MCP ile ulaşmayı dener + aktif kontrol** |
| 11 | Platform Desteği | **Tüm platformlar ilk sürümde** (VS Code, Antigravity, Codex CLI, Cursor, Windsurf) |
| 12 | Authentication | **API key + device pairing** |
| 13 | Ajan İzolasyonu | **Agent-level data partition** (SQLite FK + auth middleware) |
| 14 | Test Stratejisi | **Record & replay** (VCR pattern) |
| 15 | Deployment | **pip install + npm package** (her bileşen ayrı) |

### Kalan Riskler (Grill Çıktısı)
1. **Platform bakım yükü** (Q11): 5 platform aynı anda — MCP standardı ile minimize edilmeli
2. **Plugin-level cron consistency** (Q10): Core'un aktif agent kontrolü yapması kararlaştırıldı
3. **VCR test bakımı** (Q14): Provider API değişikliklerinde otomatik cassette yenileme düşünülmeli
4. **pip + npm deployment** (Q15): İki ayrı package manager version uyumu

---

## Bağımlılıklar / Dependencies

### Backend (Python)
- FastAPI
- uvicorn
- SQLAlchemy + aiosqlite (dev) / asyncpg (prod)
- pydantic
- anthropic, openai, google-generativeai
- ollama (yerel modeller için)
- mcp (Python MCP SDK)
- cryptography (AES-256-GCM)
- alembic (migrasyon)

### Frontend (TypeScript)
- React 19
- TypeScript 5.x
- Vite
- @vscode/webview-ui-toolkit
- websocket (WebSocket istemcisi)

### Platform Plugin (TypeScript)
- @vscode/extension API
- vsce (packaging)

---

## Referans Alınan Projeler / Reference Projects

| Proje | Alınan Pattern | AgentManager Modülü |
|-------|---------------|---------------------|
| **agentclaw** | Telegram/Discord kanalları, cron registry, memory, skill, SOUL/USER | Bot, Scheduler, Memory |
| **appflowy** | PluginSandbox, MCP Client, LocalAI, stream events, feature flags | Plugin Sistemi, MCP |
| **lobe-chat** | Multi-provider yönetimi, plugin registry, Ollama integration, UI | Provider'lar, Panel UI |
| **my-SuperAGI** | Tool registry, concurrent workers, resource manager, looping detection | Tool Sistemi, Worker Pool |
| **Auto-GPT** | Chain-of-thought, memory backends, continuous mode, CLI flags | Log Sistemi, CLI |
| **aider** | Git integration, repo-map, in-chain chat commands, VCR testing | Git Tool, Komut Dili |
| **AgentGPT** | Goal-based task loop, Prisma schema, UX patterns | Task Queue, Panel UX |

---

## Bilinen Sorunlar / Known Issues

1. Yok (henüz geliştirme başlamadı)

---

## Notlar / Notes

- Tüm tasarım kararları grill testinden geçti (15 soru)
- PRD Issue #1'de yayında
- 13 repo analiz edildi, 7'sinden pattern alınıyor
- 5 paralel track ile maksimum parallelism hedefleniyor
- agentic yapı: her track bağımsız sub-agent olarak çalışabilir
