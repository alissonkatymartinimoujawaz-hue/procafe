import subprocess, time, re, csv, html
rows=[]; log=open('FETCH_LOG.md','a')
log.write('# FETCH_LOG ihcafe_docs4\n\n| URL | HTTP | note |\n|---|---|---|\n')
fails=0
for y in range(2018,2027):
    for m in range(1,13):
        if (y,m)>(2026,9): continue
        u=f'https://www.ihcafe.hn/wp-content/uploads/{y}/{m:02d}/'
        out=f'listings/{y}_{m:02d}.html'
        r=subprocess.run(['curl','-sS','-L','--max-redirs','0','-m','25','-A','Mozilla/5.0','-o',out,'-w','%{http_code}',u],capture_output=True,text=True)
        code=r.stdout.strip() or '000'
        s=open(out,errors='replace').read() if code=='200' else ''
        files=re.findall(r'<a href="([^"?/][^"]*)">[^<]*</a>\s*</td>\s*<td[^>]*>([^<]*)</td>\s*<td[^>]*>([^<]*)</td>',s)
        if not files: files=[(f,'','') for f in re.findall(r'<a href="([^"?/][^"]*)"',s)]
        for f,d,sz in files: rows.append((y,m,html.unescape(f),sz.strip(),d.strip()))
        log.write(f'| {u} | {code} | {len(files)} entries {r.stderr.strip()[:80]} |\n'); log.flush()
        print(y,m,code,len(files),flush=True)
        time.sleep(1)
with open('listing.csv','w',newline='') as fh:
    w=csv.writer(fh); w.writerow(['year','month','filename','size','modified']); w.writerows(rows)
