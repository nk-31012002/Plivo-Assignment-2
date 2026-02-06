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

# 🔎 API Verification

## 📌 REST APIs (Topic Management & Observability)

### ➕ Create a Topic

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/topics" `
  -Method Post `
  -Body '{"name": "orders"}' `
  -ContentType "application/json"
```

### 📋 List Topics

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/topics" `
  -Method Get
```

### 📊 Check Service Stats

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/stats" `
  -Method Get
```

### ❤️ Health Check

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/health" `
  -Method Get
```

---

# 🔌 WebSocket API (Real-time Messaging)

### 📍 Endpoint

```
ws://localhost:8000/ws
```

### 📦 Supported Payload Types

- `subscribe`
- `unsubscribe`
- `publish`
- `ping`
