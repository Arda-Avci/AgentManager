
<p align="center">
  <img src="https://placehold.co/120x120/1a1a2e/eee?text=AM" alt="AgentManager Logo" width="120" height="120"/>
</p>

<h1 align="center">AgentManager</h1>

<p align="center">
  <b>Çoklu-Ajan Orkestrasyon Eklentisi</b><br>
  <b>Multi-Agent Orchestration Plugin</b>
</p>

<p align="center">
  <i>Tüm yapay zeka modelleri için evrensel ajan yönetimi</i><br>
  <i>Universal agent management for all AI models</i>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white">
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white">
  <img alt="React" src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-purple">
</p>

---

## 🇹🇷 Türkçe

### AgentManager Nedir?

**AgentManager**, birden çok yapay zeka modelini (Claude, Gemini, GPT, Ollama, OpenRouter...) tek bir çatı altında yönetmenizi sağlayan, **platform-bağımsız** bir multi-agent orkestrasyon bileşenidir.

VS Code, Antigravity, Codex CLI gibi platformlara **eklenti** veya **MCP sunucusu** olarak kurulur. Ajanlarınızın durumunu canlı görebileceğiniz, duraklatıp devam ettirebileceğiniz bir web paneli sunar.

### Desteklenen Platformlar

| Platform | Tip | Durum |
|----------|-----|-------|
| **VS Code** | Extension (TypeScript + Webview) | ✅ Planlandı |
| **Antigravity** | MCP Plugin | ✅ Planlandı |
| **Codex CLI** | MCP Client | ✅ Planlandı |
| **Claude Code** | MCP Client | ✅ Planlandı |
| **OpenAI CLI** | MCP Client | 🔄 Geliştirme aşaması |
| **Diğer MCP uyumlu istemciler** | MCP Client | ✅ Uyumlu |

### Desteklenen Yapay Zeka Modelleri

| Model | Sağlayıcı | Durum |
|-------|-----------|-------|
| **GPT-4 / GPT-4o / o1** | OpenAI | ✅ Planlandı |
| **Claude 3.5 / 4** | Anthropic | ✅ Planlandı |
| **Gemini Pro / Ultra** | Google | ✅ Planlandı |
| **Tüm modeller** | OpenRouter | ✅ Planlandı |
| **Llama 3, Mistral, vb.** | Ollama (yerel) | ✅ Planlandı |
| **Özel uç noktalar** | OpenAI-uyumlu API | ✅ Planlandı |

### Nasıl Çalışır?

```
┌──────────────────────────────────────────────────┐
│  SİZ (Ana Platform)                               │
│  ├─ VS Code'da paneli açarsınız                  │
│  ├─ Antigravity'den tool çağırırsınız            │
│  └─ Codex CLI'den MCP ile bağlanırsınız          │
└──────────────────┬───────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────┐
│  AgentManager Core (Python)                       │
│  ├─ Emri alır, görevi parçalara böler            │
│  ├─ Ajan kuyruğuna dağıtır                       │
│  └─ Her ajan KENDİ modelini kullanır             │
└──────────────────┬───────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────┐
│  Ajan Havuzu                                      │
│  ├─ 👩‍⚖️ Avukat Ajan (Claude) → Mevzuat analizi     │
│  ├─ 👨‍💻 Yazılımcı Ajan (GPT-4) → Kod yazma        │
│  ├─ 🎨 Tasarımcı Ajan (Gemini) → Frontend         │
│  ├─ 🔍 Reviewer Ajan (Claude) → Kod inceleme      │
│  └─ 🧪 Tester Ajan (GPT-4) → Test                │
└──────────────────────────────────────────────────┘
```

**Önemli:** Her ajanın kendi API anahtarı ve modeli vardır. Ana platformun kotası tükenmez.

### Hızlı Kurulum

```bash
# Python core'u yükle
pip install agentmanager-core

# VS Code extension'u yükle (VS Code içinden)
# Extensions > Ara: AgentManager > Install

# Çalıştır
agentmanager start

# Web paneli aç
# http://localhost:3010
```

Detaylı kurulum için: [docs/help/kurulum.md](docs/help/kurulum.md)

### Temel Komutlar

```bash
agentmanager start          # Core'u başlat
agentmanager stop           # Core'u durdur
agentmanager status         # Durumu göster
agentmanager web            # Web paneli aç
agentmanager provider add   # LLM sağlayıcısı ekle
agentmanager agent create   # Yeni ajan oluştur
```

---

## 🇬🇧 English

### What is AgentManager?

**AgentManager** is a **platform-independent** multi-agent orchestration component that lets you manage multiple AI models (Claude, Gemini, GPT, Ollama, OpenRouter...) under one roof.

It installs as a **plugin** or **MCP server** on platforms like VS Code, Antigravity, and Codex CLI. It provides a web panel where you can monitor agent status in real-time, pause, and resume them.

### Supported Platforms

| Platform | Type | Status |
|----------|------|--------|
| **VS Code** | Extension (TypeScript + Webview) | ✅ Planned |
| **Antigravity** | MCP Plugin | ✅ Planned |
| **Codex CLI** | MCP Client | ✅ Planned |
| **Claude Code** | MCP Client | ✅ Planned |
| **OpenAI CLI** | MCP Client | 🔄 In development |
| **Other MCP clients** | MCP Client | ✅ Compatible |

### Supported AI Models

| Model | Provider | Status |
|-------|----------|--------|
| **GPT-4 / GPT-4o / o1** | OpenAI | ✅ Planned |
| **Claude 3.5 / 4** | Anthropic | ✅ Planned |
| **Gemini Pro / Ultra** | Google | ✅ Planned |
| **All models** | OpenRouter | ✅ Planned |
| **Llama 3, Mistral, etc.** | Ollama (local) | ✅ Planned |
| **Custom endpoints** | OpenAI-compatible API | ✅ Planned |

### How It Works

```
┌──────────────────────────────────────────────────┐
│  YOU (Host Platform)                              │
│  ├─ Open panel in VS Code                        │
│  ├─ Call tool from Antigravity                    │
│  └─ Connect via MCP from Codex CLI                │
└──────────────────┬───────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────┐
│  AgentManager Core (Python)                       │
│  ├─ Receives command, splits into subtasks        │
│  ├─ Distributes to agent queue                    │
│  └─ Each agent uses its OWN model                │
└──────────────────┬───────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────┐
│  Agent Pool                                       │
│  ├─ 👩‍⚖️ Lawyer Agent (Claude) → Legal analysis    │
│  ├─ 👨‍💻 Developer Agent (GPT-4) → Code writing     │
│  ├─ 🎨 Designer Agent (Gemini) → Frontend         │
│  ├─ 🔍 Reviewer Agent (Claude) → Code review      │
│  └─ 🧪 Tester Agent (GPT-4) → Testing            │
└──────────────────────────────────────────────────┘
```

**Important:** Each agent has its own API key and model. The host platform's quota is never consumed.

### Quick Start

```bash
# Install Python core
pip install agentmanager-core

# Install VS Code extension (from VS Code)
# Extensions > Search: AgentManager > Install

# Run
agentmanager start

# Open web panel
# http://localhost:3010
```

Detailed setup: [docs/help/setup.md](docs/help/setup.md)

### Basic Commands

```bash
agentmanager start          # Start the core
agentmanager stop           # Stop the core
agentmanager status         # Show status
agentmanager web            # Open web panel
agentmanager provider add   # Add LLM provider
agentmanager agent create   # Create new agent
```

---

## Mimari / Architecture

```
agentmanager/
├── core/                   # Python çekirdek / Python core
│   ├── orchestrator/       # Ajan orkestrasyonu
│   ├── agents/             # Ajan tanımları ve şablonları
│   ├── llm/                # LLM sağlayıcı yönlendirici
│   │   └── providers/      # OpenAI, Anthropic, Google, Ollama...
│   ├── state/              # Veritabanı ve durum yönetimi
│   ├── websocket/          # Gerçek zamanlı iletişim
│   ├── mcp/                # MCP sunucusu
│   └── api/                # REST API
├── plugin/                 # Platform eklentileri (TypeScript)
│   ├── vscode/             # VS Code Extension
│   ├── antigravity/        # Antigravity plugin
│   └── web-panel/          # React web arayüzü
└── docs/                   # Dökümantasyon
    └── help/               # Kullanıcı yardım dökümanları
```

---

## Dokümantasyon / Documentation

| 🇹🇷 Türkçe | 🇬🇧 English |
|------------|-------------|
| [Kurulum Kılavuzu](docs/help/kurulum.md) | [Setup Guide](docs/help/setup.md) |
| [Kullanım Kılavuzu](docs/help/kullanim.md) | [Usage Guide](docs/help/usage.md) |
| [Ajan Yönetimi](docs/help/ajan-yonetimi.md) | [Agent Management](docs/help/agent-management.md) |
| [SSS](docs/help/sss.md) | [FAQ](docs/help/faq.md) |
| [Tasarım Dokümanı](docs/2026-06-11-agentmanager-plugin-design.md) | [Design Document](docs/2026-06-11-agentmanager-plugin-design.md) |

---

## Geliştirme / Development

```bash
# Backend
cd core
pip install -r requirements.txt
uvicorn agentmanager.core.main:app --reload --port 3010

# Web Panel
cd plugin/web-panel
npm install
npm run dev

# VS Code Extension
cd plugin/vscode
npm install
code .
F5 (Run Extension)
```

Daha fazla bilgi için: [AGENTS.md](AGENTS.md) ve [Project_Plan.md](Project_Plan.md)

---

<p align="center">
  <sub>
    AgentManager — Tüm yapay zeka modelleri için multi-agent orkestrasyon<br>
    Multi-agent orchestration for all AI models
  </sub>
</p>
