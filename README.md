# 🚀 Plivo PubSub Service

## 🐳 How to Run

### 1️⃣ Build the Docker Image

```powershell
docker build -t plivo-pubsub .
```

### 2️⃣ Run the Container

```powershell
docker run -p 8000:8000 plivo-pubsub
```

The service will be available at:

```
http://localhost:8000
```

---

# 🔐 Authentication

This service implements **Basic Authentication via an API Key**.

**API Key:**
```
plivo_secret_123
```


# 🔎 API Verification

## 📌 REST APIs (Topic Management & Observability)

### ➕ Create a Topic

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/topics" `
  -Method Post `
  -Headers @{"X-API-Key"="plivo_secret_123"} `
  -Body '{"name": "orders"}' `
  -ContentType "application/json"
```

### 📋 List Topics

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/topics" `
  -Method Get `
  -Headers @{"X-API-Key"="plivo_secret_123"}
```

### 📊 Check Service Stats

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/stats" `
  -Method Get `
  -Headers @{"X-API-Key"="plivo_secret_123"}
```

### ❤️ Health Check

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/health" `
  -Method Get `
  -Headers @{"X-API-Key"="plivo_secret_123"}
```

---

# 🔌 WebSocket API (Real-time Messaging)

### 📍 Endpoint

```
ws://localhost:8000/ws?token=plivo_secret_123
```

### 📦 Supported Payload Types

- `subscribe`
- `unsubscribe`
- `publish`
- `ping`
