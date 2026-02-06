import asyncio
import time
from typing import Dict, Set, List

class PubSubHub:
    def __init__(self):
        self.topics: Dict[str, Set[asyncio.Queue]] = {}
        self.stats: Dict[str, Dict[str, int]] = {}
        self.history: Dict[str, List[dict]] = {} 
        self.start_time = time.time()

    def create_topic(self, name: str) -> bool:
        if name in self.topics:
            return False
        self.topics[name] = set()
        self.stats[name] = {"messages": 0, "subscribers": 0}
        self.history[name] = []
        return True

    def delete_topic(self, name: str) -> bool:
        if name in self.topics:
            info_event = {
                "type": "info",
                "topic": name,
                "msg": "topic_deleted",
                "ts": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
            for q in self.topics[name]:
                try:
                    q.put_nowait(info_event)
                except asyncio.QueueFull:
                    pass
            
            del self.topics[name]
            del self.stats[name]
            del self.history[name]
            return True
        return False

    def get_stats(self) -> dict:
        return {
            name: {
                "messages": data["messages"],
                "subscribers": len(self.topics[name])
            }
            for name, data in self.stats.items()
        }

    async def publish(self, topic_name: str, event: dict):
        if topic_name not in self.topics:
            return
        
        self.stats[topic_name]["messages"] += 1
        
        # Maintain history for last_n replay
        self.history[topic_name].append(event)
        if len(self.history[topic_name]) > 100:
            self.history[topic_name].pop(0)
            
        # Fan-out to all active subscriber queues
        for q in self.topics[topic_name]:
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                # Backpressure: Drop oldest policy
                try:
                    q.get_nowait()
                    q.put_nowait(event)
                except:
                    pass

hub = PubSubHub()