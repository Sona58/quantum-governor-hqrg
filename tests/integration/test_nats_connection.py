# -*- coding: utf-8 -*-

import pytest
import asyncio
from nats.aio.client import Client as NATS

@pytest.mark.asyncio
async def test_nats_pub_sub():
    nc = NATS()
    await nc.connect("nats://localhost:4222")
    
    # Test publishing a dummy risk request
    js = nc.jetstream()
    ack = await js.publish("quantum.test", b'{"data": "test"}')
    
    assert ack.seq > 0
    await nc.close()