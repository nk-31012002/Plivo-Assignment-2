## How to Run

1. **Build the Docker Image**:
   ```powershell
   docker build -t plivo-pubsub .

2. **Run the Container**
   docker run -p 8000:8000 plivo-pubsub

## API Verification Commands

**REST (Topic Management & Observability)**

***Create Topic:***
```Invoke-RestMethod -Uri "http://localhost:8000/topics" -Method Post -Body '{"name": "orders"}' -ContentType "application/json"```

***List Topics:***
```Invoke-RestMethod -Uri "http://localhost:8000/topics" -Method Get```

***Check Stats:***
```Invoke-RestMethod -Uri "http://localhost:8000/stats" -Method Get```

***Health Check:***
```Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get```

## WebSocket (Messaging)

***Endpoint:***
```ws://localhost:8000/ws```

***Payload Types:*** 
```subscribe, unsubscribe, publish, ping```

