# -*- coding: utf-8 -*-

import uuid
import time

class MockSlurmProvider:
    def submit_job(self, data_payload):
        job_id = f"slurm-{uuid.uuid4()}"
        # Log the submission for visibility in the Gateway logs
        print(f"🏛️ [HPC-ROUTER] Routing complex circuit to SLURM. Job ID: {job_id}")
        
        # Simulate network latency to the HPC head node
        time.sleep(0.2) 
        
        return {
            "job_id": job_id,
            "status": "SUBMITTED",
            "provider": "SLURM_HPC_CLUSTER"
        }

    def get_status(self, job_id):
        return "RUNNING"