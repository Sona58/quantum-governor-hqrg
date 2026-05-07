# -*- coding: utf-8 -*-

import pytest
import os
from nats.aio.client import Client as NATS

@pytest.mark.asyncio
async def test_nats_pub_sub():
    nats_url = os.getenv("NATS_URL", "nats://localhost:4222")
    nc = NATS()
    await nc.connect(nats_url)
    
    js = nc.jetstream()
    # Use a subject that matches the QUANTUM stream pattern
    ack = await js.publish("quantum.test", b'{"data": "test"}')
    
    assert ack.seq > 0
    await nc.close()