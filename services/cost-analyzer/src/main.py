# -*- coding: utf-8 -*-

import asyncio
import json
import nats
import redis
import os
from .accounting import QuantumAccountant

class CostAnalyzer:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis-service"),
            port=6379,
            decode_responses=True
        )
        self.accountant = QuantumAccountant()

    async def run(self):
        nc = await nats.connect(os.getenv("NATS_URL", "nats://nats-service:4222"))
        print("Cost Analyzer connected to NATS")

        async def result_handler(msg):
            data = json.loads(msg.data.decode())
            request_id = data.get("request_id")
            engine = data.get("metrics", {}).get("engine")
            latency = data.get("metrics", {}).get("latency", 0)

            # 1. Calculate the cost
            cost = self.accountant.calculate_cost(engine, latency)
            
            # 2. Update Redis (Deduct from user balance)
            # In a real app, 'user_id' would be passed through the NATS headers
            # Here we just log it for the "Business Transparency" requirement
            print(f"[$] Billing Audit | Request: {request_id} | Engine: {engine} | Cost: {cost} Credits")
            
            # Update a global 'total_spend' counter for our Grafana dashboard
            self.redis_client.incrbyfloat("stats:total_quantum_spend", cost)
            self.redis_client.set(f"audit:{request_id}:cost", cost)

        # Listen for results from ANY engine
        await nc.subscribe("results.*", cb=result_handler)

        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    analyzer = CostAnalyzer()
    asyncio.run(analyzer.run())