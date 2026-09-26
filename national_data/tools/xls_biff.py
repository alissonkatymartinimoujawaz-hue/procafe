# Minimal stdlib reader for legacy .xls (BIFF8 in OLE2). Usage: python3 xls_biff.py file.xls [sheet]
import struct,sys
def ole_stream(data,name='Workbook'):
    ss=1<<struct.unpack_from('<H',data,30)[0]
    mss=1<<struct.unpack_from('<H',data,32)[0]
    nfat=struct.unpack_from('<I',data,44)[0]
    dirstart=struct.unpack_from('<I',data,48)[0]
    minicut=struct.unpack_from('<I',data,56)[0]
    minifatstart=struct.unpack_from('<I',data,60)[0]
    difstart=struct.unpack_from('<I',data,68)[0]
    ndif=struct.unpack_from('<I',data,72)[0]
    difat=list(struct.unpack_from('<109I',data,76))
    s=difstart
    for _ in range(ndif):
        off=512+s*ss; ents=struct.unpack_from('<%dI'%(ss//4),data,off)
        difat+=ents[:-1]; s=ents[-1]
    difat=[x for x in difat[:nfat]]
    fat=[]
    for sec in difat:
        fat+=struct.unpack_from('<%dI'%(ss//4),data,512+sec*ss)
    def chain(st):
        out=[];seen=set()
        while st<0xFFFFFFFA and st not in seen:
            seen.add(st); out.append(data[512+st*ss:512+(st+1)*ss]); st=fat[st]
        return b''.join(out)
    d=chain(dirstart)
    ents=[]
    for i in range(len(d)//128):
        e=d[i*128:(i+1)*128]; nl=struct.unpack_from('<H',e,64)[0]
        nm=e[:max(nl-2,0)].decode('utf-16le',errors='replace')
        ents.append((nm,e[66],struct.unpack_from('<I',e,116)[0],struct.unpack_from('<I',e,120)[0]))
    for nm,t,st,sz in ents:
        if nm in (name,'Book'):
            if sz<minicut:
                raise Exception('mini')
            return chain(st)[:sz]
    raise Exception('no workbook')
def rk(v):
    if v&2: x=float(v>>2 if not v&0x80000000 else (v>>2)-(1<<30))
    else: x=struct.unpack('<d',struct.pack('<Q',(v&0xFFFFFFFC)<<32))[0]
    return x/100 if v&1 else x
def parse(fn):
    wb=ole_stream(open(fn,'rb').read())
    recs=[];p=0
    while p+4<=len(wb):
        rid,ln=struct.unpack_from('<HH',wb,p); recs.append((rid,wb[p+4:p+4+ln],p)); p+=4+ln
    sheets=[];sst=[]
    # SST with continues
    for i,(rid,b,p0) in enumerate(recs):
        if rid==0x85:
            off=struct.unpack_from('<I',b,0)[0]; nl=b[6]; fl=b[7]
            nm=b[8:8+nl*(2 if fl&1 else 1)].decode('utf-16le' if fl&1 else 'latin-1')
            sheets.append((nm,off))
        if rid==0xFC:
            parts=[b]; j=i+1
            while recs[j][0]==0x3C: parts.append(recs[j][1]); j+=1
            sst=read_sst(parts)
    out={}
    offs={p0:k for k,(rid,b,p0) in enumerate(recs)}
    for nm,off in sheets:
        k=offs[off]; cells={}; last=None
        for rid,b,p0 in recs[k+1:]:
            if rid==0x0A: break
            if rid==0xFD:
                r,c,_,ix=struct.unpack_from('<HHHI',b); cells[(r,c)]=sst[ix]
            elif rid==0x203:
                r,c,_=struct.unpack_from('<HHH',b); cells[(r,c)]=struct.unpack_from('<d',b,6)[0]
            elif rid==0x27E:
                r,c,_,v=struct.unpack_from('<HHHI',b); cells[(r,c)]=rk(v)
            elif rid==0xBD:
                r,c=struct.unpack_from('<HH',b); n=(len(b)-6)//6
                for q in range(n):
                    v=struct.unpack_from('<I',b,4+q*6+2)[0]; cells[(r,c+q)]=rk(v)
            elif rid==0x06:
                r,c,_=struct.unpack_from('<HHH',b)
                if b[12:14]==b'\xff\xff':
                    if b[6]==0: last=(r,c)
                else: cells[(r,c)]=struct.unpack_from('<d',b,6)[0]
            elif rid==0x207 and last:
                n=struct.unpack_from('<H',b)[0]; fl=b[2]
                cells[last]=b[3:3+n*(2 if fl&1 else 1)].decode('utf-16le' if fl&1 else 'latin-1',errors='replace'); last=None
            elif rid==0x204:
                r,c,_,n=struct.unpack_from('<HHHH',b); fl=b[8]
                cells[(r,c)]=b[9:9+n*(2 if fl&1 else 1)].decode('utf-16le' if fl&1 else 'latin-1',errors='replace')
        out[nm]=cells
    return out
def read_sst(parts):
    b=parts[0]; total,uniq=struct.unpack_from('<II',b); pi=0; pos=8; res=[]
    cur=parts
    def need():
        nonlocal b,pos,pi
        if pos>=len(b): pi+=1; b=cur[pi]; pos=0
    for _ in range(uniq):
        need()
        n=struct.unpack_from('<H',b,pos)[0]; fl=b[pos+2]; pos+=3
        rt=0;sz=0
        if fl&8: rt=struct.unpack_from('<H',b,pos)[0]; pos+=2
        if fl&4: sz=struct.unpack_from('<I',b,pos)[0]; pos+=4
        s=[];rem=n;wide=fl&1
        while rem>0:
            if pos>=len(b):
                pi+=1; b=cur[pi]; wide=b[0]&1; pos=1
            w=2 if wide else 1
            avail=(len(b)-pos)//w; k=min(avail,rem)
            s.append(b[pos:pos+k*w].decode('utf-16le' if wide else 'latin-1',errors='replace')); pos+=k*w; rem-=k
        res.append(''.join(s))
        skip=rt*4+sz
        while skip>0:
            if pos>=len(b): pi+=1; b=cur[pi]; pos=0
            k=min(skip,len(b)-pos); pos+=k; skip-=k
    return res
def col(c):
    s=''
    c+=1
    while c: c,r=divmod(c-1,26); s=chr(65+r)+s
    return s
if __name__=='__main__':
    o=parse(sys.argv[1])
    if len(sys.argv)==2:
        for k in o: print(k)
    else:
        cells=o[sys.argv[2]]
        rows={}
        for (r,c),v in cells.items(): rows.setdefault(r,{})[col(c)]=v
        for r in sorted(rows): print(r+1,dict(sorted(rows[r].items(),key=lambda x:(len(x[0]),x[0]))))
