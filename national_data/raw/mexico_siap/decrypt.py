import re,sys,hashlib,struct
import subprocess
src,dst=sys.argv[1],sys.argv[2]
d=open(src,'rb').read()
PAD=bytes.fromhex('28BF4E5E4E758A4164004E56FFFA01082E2E00B6D0683E802F0CA9FE6453697A')
def lit(s):
    # parse PDF literal string starting at '('
    out=bytearray();i=1;depth=1
    while True:
        c=s[i]
        if c==0x5c:
            n=s[i+1]
            m={ord('n'):10,ord('r'):13,ord('t'):9,ord('b'):8,ord('f'):12,ord('('):40,ord(')'):41,0x5c:0x5c}
            if n in m: out.append(m[n]); i+=2; continue
            if 48<=n<=55:
                j=i+1;v=''
                while j<i+4 and 48<=s[j]<=55: v+=chr(s[j]); j+=1
                out.append(int(v,8)&255); i=j; continue
            if n in (10,13): i+=2; continue
            out.append(n); i+=2; continue
        if c==0x28: depth+=1
        if c==0x29:
            depth-=1
            if depth==0: return bytes(out)
        out.append(c); i+=1
i=d.find(b'/Filter/Standard'); st=d.rfind(b'obj',0,i); en=d.find(b'endobj',i); enc=d[st:en]
O=lit(enc[enc.find(b'/O(')+2:]); P=int(re.search(rb'/P (-?\d+)',enc).group(1))
ID=bytes.fromhex(re.search(rb'/ID\s*\[\s*<([0-9A-Fa-f]+)>',d).group(1).decode())
L=int(re.search(rb'/Length (\d+)/P',enc).group(1)) if re.search(rb'/Length (\d+)/P',enc) else 128
n=L//8
h=hashlib.md5(PAD+O[:32]+struct.pack('<i',P)+ID)
k=h.digest()
for _ in range(50): k=hashlib.md5(k[:n]).digest()
key=k[:n]
print('keylen',n)
encnum=int(d[st-20:st].split()[-2])
def dec(num,gen,data):
    ok=hashlib.md5(key+struct.pack('<I',num)[:3]+struct.pack('<I',gen)[:2]+b'sAlT').digest()[:16]
    if len(data)<32 or len(data)%16: return data
    p=subprocess.run(['openssl','enc','-d','-aes-128-cbc','-nopad','-K',ok.hex(),'-iv',data[:16].hex()],input=data[16:],capture_output=True).stdout
    return p[:-p[-1]] if 1<=p[-1]<=16 else p
out=bytearray(b'%PDF-1.6\n')
cnt=0
for m in re.finditer(rb'(\d+)\s+(\d+)\s+obj\b(.*?)\bendobj',d,re.S):
    num,gen,body=int(m.group(1)),int(m.group(2)),m.group(3)
    sm=re.search(rb'stream\r?\n',body)
    if sm and num!=encnum and b'/XRef' not in body[:sm.start()]:
        head=body[:sm.start()]; raw=body[sm.end():]
        lm=re.search(rb'/Length (\d+)(?!\s+\d+\s+R)',head)
        if lm: raw=raw[:int(lm.group(1))]
        else: raw=raw[:raw.rfind(b'endstream')].rstrip(b'\r\n')
        p=dec(num,gen,raw); cnt+=1
        head=re.sub(rb'/Length \d+(\s+\d+\s+R)?',b'/Length %d'%len(p),head,1)
        body=head+b'stream\n'+p+b'\nendstream\n'
    out+=b'%d %d obj'%(num,gen)+body+b'endobj\n'
open(dst,'wb').write(out); print('streams',cnt)
