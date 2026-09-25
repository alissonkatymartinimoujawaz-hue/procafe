import subprocess, time, sys, re, urllib.parse
urls=[l.strip() for l in open(sys.argv[1]) if l.strip()]
NOFOLLOW=len(sys.argv)>3; start=int(sys.argv[2]); last={}; blocked=set()
log=open('FETCH_LOG.md','a')
for i,u in enumerate(urls,start):
    h=urllib.parse.urlparse(u).netloc
    if h in blocked: log.write(f'| {u} | skipped | host blocked earlier |\n'); continue
    if h in last: time.sleep(max(0,1-(time.time()-last[h])))
    ext='.pdf' if u.lower().endswith('.pdf') else ('.xlsx' if u.lower().endswith('.xlsx') else '.html')
    name=f'{i:03d}_'+re.sub(r'[^A-Za-z0-9.-]+','_',h+urllib.parse.urlparse(u).path).strip('_')[:90]
    name=re.sub(r'\.(pdf|xlsx|html)$','',name,flags=re.I)+ext
    r=subprocess.run((['curl','-sS'] if NOFOLLOW else ['curl','-sS','-L'])+['-m','60','-A','Mozilla/5.0 (X11; Linux x86_64) Chrome/124 Safari/537.36','-o',name,'-w','%{http_code} %{content_type} %{size_download} %{url_effective}',u],capture_output=True,text=True)
    last[h]=time.time()
    code=(r.stdout.split() or ['000'])[0]
    if code in ("000","403","407") and "tunnel" in r.stderr and h in r.stdout: blocked.add(h)
    if code!='200':
        subprocess.run(['rm','-f',name])
    log.write(f'| {u} | {code} | {" ".join(r.stdout.split()[1:])} {r.stderr.strip()[:100]} -> {name if code=="200" else "-"} |\n'); log.flush()
    print(code,name,r.stderr.strip()[:80],flush=True)
