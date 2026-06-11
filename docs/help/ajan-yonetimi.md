# Ajan Yönetimi

## Ajan Rolleri

AgentManager varsayılan olarak 5 rol ile gelir:

| Rol | Açıklama | Varsayılan Yetenekler |
|-----|----------|----------------------|
| **lawyer** | Yasal mevzuat analizi, uyumluluk denetimi | KVKK, GDPR, sözleşme analizi |
| **developer** | Backend kod geliştirme, API tasarımı | Python, TypeScript, SQL, REST |
| **frontend** | Kullanıcı arayüzü geliştirme | React, Tailwind, CSS, UX |
| **reviewer** | Kod inceleme, güvenlik denetimi | Code review, güvenlik analizi |
| **tester** | Test senaryoları, entegrasyon testi | Unit test, entegrasyon testi, E2E |

## Ajan Oluşturma

### Web Panelinden
1. "Yeni Ajan" butonuna tıklayın
2. İsim, rol ve model seçin
3. İsteğe bağlı: özel sistem talimatı girin
4. "Oluştur"a tıklayın

### CLI ile

```bash
agentmanager agent create \
  --name "Backend-Dev" \
  --role developer \
  --provider my-openai \
  --model gpt-4 \
  --system-prompt "Backend geliştirme uzmanısın..."
```

### MCP ile (Antigravity/Codex CLI)

```
create_agent(name="Backend-Dev", role="developer", provider="my-openai", model="gpt-4")
```

## Ajan Yönetimi

### Duraklatma ve Devam Ettirme

Bir ajanı duraklattığınızda:
- Mevcut görevi **dondurulur** (state korunur)
- LLM çağrısı varsa tamamlanması beklenir
- Diğer ajanlar etkilenmez

Devam ettirdiğinizde:
- Kaldığı yerden devam eder
- Chain-of-thought kaybolmaz

### Rol Değiştirme

Bir ajanın rolünü runtime'da değiştirebilirsiniz:

```bash
agentmanager agent update Backend-Dev --role reviewer
```

Bu işlem:
- Ajanın sistem talimatını yeni role göre günceller
- Mevcut görevi varsa tamamlanmasını bekler
- Bir sonraki görevde yeni rol aktif olur

### Model Değiştirme

```bash
agentmanager agent update Backend-Dev --model claude-4 --provider my-claude
```

Bu işlem:
- Yeni model hemen aktif olur
- Devam eden görev varsa mevcut modelle tamamlanır
- Token sayacı sıfırlanmaz

## Ajan Silme

```bash
agentmanager agent remove Backend-Dev
```

Silinen ajanın:
- Tüm görev geçmişi arşivlenir (silinmez)
- Aktif görevi varsa önce iptal edilir
- Kaydı veritabanından kaldırılır

## Özel Rol Oluşturma

Web panelindeki "Rol Yöneticisi"nden veya doğrudan şablon dosyası oluşturarak:

```yaml
# core/agents/templates/data-analyst.yaml
name: data-analyst
display_name: Veri Analisti
description: Veri analizi, raporlama ve görselleştirme
system_prompt: |
  Sen bir veri analisti asistanısın.
  Görevin: veri setlerini analiz etmek, anlamlı içgörüler çıkarmak
  ve görsel raporlar hazırlamak.
capabilities:
  - veri analizi
  - görselleştirme
  - raporlama
default_model: gpt-4
```

## Ajan İletişimi

Ajanlar arasında doğrudan iletişim yoktur. İletişim şöyle işler:

```
SİZ → Ajan-1'e görev atar
SİZ → Ajan-1'in çıktısını alır
SİZ → Ajan-2'ye Ajan-1'in çıktısını girdi olarak verir
```

Bu model sayesinde:
- Her ajan izole çalışır
- Token tüketimi kontrol altındadır
- Hata bir ajandan diğerine yayılmaz
- Prompt injection riski azalır
