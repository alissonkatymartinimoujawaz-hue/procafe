"""fetch(url, stem) -> (code, final_url, ctype, path). Logs to FETCH_LOG.md. Standard library + curl."""
import subprocess, time, re, os, urllib.parse
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36'
_last={}; blocked=set()
if not os.path.exists('FETCH_LOG.md'):
    open('FETCH_LOG.md','w').write('# Fetch log\n\n| URL | HTTP | final URL | content-type | saved as / error |\n|---|---|---|---|---|\n')
def ext_for(ct, cd, url):
    m=re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)',cd or '',re.I)
    if m and '.' in m.group(1): return '.'+m.group(1).rsplit('.',1)[1].lower().strip()
    ct=(ct or '').lower()
    for k,v in [('pdf','.pdf'),('spreadsheetml','.xlsx'),('ms-excel','.xls'),('wordprocessing','.docx'),('msword','.doc'),('json','.json'),('html','.html'),('zip','.zip'),('image/jpeg','.jpg'),('image/png','.png'),('powerpoint','.ppt'),('presentationml','.pptx')]:
        if k in ct: return v
    p=urllib.parse.urlparse(url).path
    return os.path.splitext(p)[1] or '.bin'
def fetch(url, stem, timeout=60):
    h=urllib.parse.urlparse(url).netloc
    if h in blocked:
        log(url,'skip','','','host blocked earlier'); return ('skip',None,None,None)
    if h in _last: time.sleep(max(0,1-(time.time()-_last[h])))
    tmp=stem+'.part'; hdr=stem+'.hdr'
    r=subprocess.run(['curl','-sS','-L','-m',str(timeout),'-A',UA,'-D',hdr,'-o',tmp,'-w','%{http_code}\t%{url_effective}\t%{content_type}',url],capture_output=True,text=True)
    _last[h]=time.time()
    parts=(r.stdout.split('\t')+['','',''])[:3]; code,final,ct=parts
    cd=''
    try:
        for l in open(hdr,errors='ignore'):
            if l.lower().startswith('content-disposition'): cd=l
    except Exception: pass
    for f in (hdr,):
        if os.path.exists(f): os.remove(f)
    path=None
    if code=='200' and os.path.exists(tmp) and os.path.getsize(tmp)>0:
        path=stem+ext_for(ct,cd,final); os.replace(tmp,path)
    else:
        if os.path.exists(tmp): os.remove(tmp)
        if 'tunnel' in r.stderr or 'proxy' in r.stderr.lower():
            blocked.add(h)
    log(url,code,final,ct,path or r.stderr.strip()[:120])
    return (code,final,ct,path)
def log(url,code,final,ct,note):
    with open('FETCH_LOG.md','a') as f: f.write(f'| {url} | {code} | {final} | {ct} | {note} |\n')
