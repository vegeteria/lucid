import asyncio
import os
import uuid

async def run_lucida(url, cf_clearance, user_agent, proxy, progress_cb):
    temp_dir = f"/tmp/{uuid.uuid4().hex}"
    os.makedirs(temp_dir, exist_ok=True)
    
    cmd = [
        "/usr/local/bin/lucida",
        "--output", temp_dir,
        "--flatten-directories"
    ]
    if cf_clearance:
        cmd.extend(["--cf-clearance", cf_clearance])
    if user_agent:
        cmd.extend(["--user-agent", user_agent])
    cmd.append(url)
    
    env = os.environ.copy()
    if proxy:
        env["ALL_PROXY"] = proxy
        env["HTTP_PROXY"] = proxy
        env["HTTPS_PROXY"] = proxy
        
    process = await asyncio.create_subprocess_exec(
        *cmd,
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    
    while True:
        line = await process.stdout.readline()
        if not line:
            break
        text = line.decode('utf-8').strip()
        if text:
            await progress_cb(text)
            
    await process.wait()
    return temp_dir, process.returncode
