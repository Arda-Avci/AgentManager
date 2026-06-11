# Kullanım Kılavuzu

## Hızlı Başlangıç

AgentManager'i kurduktan sonra aşağıdaki adımları izleyin:

### 1. LLM Sağlayıcısı Ekleme

```bash
agentmanager provider add
# Ad: my-openai
# Tip: openai
# API Anahtarı: sk-xxx
# Varsayılan model: gpt-4
```

Birden çok sağlayıcı ekleyebilirsiniz:

```bash
agentmanager provider add --name my-claude --type anthropic --key sk-ant-xxx
agentmanager provider add --name local-llama --type ollama --url http://localhost:11434
agentmanager provider add --name router --type openrouter --key sk-or-xxx
```

### 2. Ajan Oluşturma

Web panelinden veya CLI ile:

```bash
agentmanager agent create \
  --name "Avukat-1" \
  --role lawyer \
  --provider my-claude \
  --model claude-3-opus
```

```bash
agentmanager agent create \
  --name "Yazilimci-1" \
  --role developer \
  --provider my-openai \
  --model gpt-4
```

### 3. Görev Atama

```bash
agentmanager task assign \
  --agent Avukat-1 \
  --input "KVKK kapsamında veri işleme şartlarını analiz et"
```

### 4. İzleme

Web panelini açın: `http://localhost:3010`

Panelde şunları görebilirsiniz:
- Tüm ajanların anlık durumu
- Ajanların düşünce zinciri (chain-of-thought) canlı akışı
- Token kullanımı ve kota bilgisi
- Görev geçmişi

## Web Panel Kullanımı

### Ajan Kartları
Her ajan bir kart olarak görüntülenir:
- **İsim** ve **rol** rozeti
- **Model** ve **sağlayıcı** bilgisi
- **Durum** göstergesi (🟢 çalışıyor / 🟡 beklemede / 🔴 hata / ⏸ duraklatıldı)
- Son görev özeti
- Kontrol butonları (▶ başlat / ⏸ duraklat / ⏹ durdur)

### Canlı Log Akışı
Bir ajana tıkladığınızda detay modalı açılır:
- **Chain-of-Thought**: Ajanın o anki düşünce süreci
- **LLM Logları**: API çağrıları, token sayımı
- **Zaman Çizelgesi**: Görevin adım adım ilerlemesi

### Sağlayıcı Yönetimi
- Yeni API anahtarı ekleme
- Mevcut anahtarları düzenleme/silme
- Her ajan için farklı sağlayıcı/model atama

## MCP Kullanımı (AI Platformları İçin)

Antigravity, Codex CLI veya Claude Code gibi platformlardan ajanları yönetmek için MCP tools:

```
list_agents → Tüm ajanları listele
assign_task(agent_id="avukat-1", input="...") → Görev ata
pause_agent(agent_id="yazilimci-1") → Ajanı duraklat
resume_agent(agent_id="yazilimci-1") → Devam ettir
```

## Komut Satırı Referansı

```bash
agentmanager
├── start           Core'u başlat
├── stop            Core'u durdur
├── restart         Core'u yeniden başlat
├── status          Durum bilgisi
├── web             Web panelini aç
│
├── provider
│   ├── add         Yeni sağlayıcı ekle
│   ├── list        Sağlayıcıları listele
│   ├── update      Sağlayıcı güncelle
│   └── remove      Sağlayıcı sil
│
├── agent
│   ├── create      Yeni ajan oluştur
│   ├── list        Ajanları listele
│   ├── show        Ajan detayı
│   ├── update      Ajan güncelle
│   ├── remove      Ajan sil
│   ├── pause       Ajanı duraklat
│   └── resume      Ajanı devam ettir
│
└── task
    ├── assign      Görev ata
    ├── list        Görevleri listele
    └── cancel      Görevi iptal et
```
