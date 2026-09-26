import sys,re
sys.path.insert(0,'/home/user/procafe/national_data/tools')
from pdftext import PDF,page_items
fn=sys.argv[1]; pages=[int(x) for x in sys.argv[2].split(',')]; ytol=float(sys.argv[3]) if len(sys.argv)>3 else 4
p=PDF(open(fn,'rb').read()); pg=p.pages()
for i in pages:
    n,res=pg[i-1]
    xo=p.dict_inline_or_ref(res,b'XObject')
    for name,ref in re.findall(rb'/(\S+?)\s+(\d+)\s+0\s+R',xo):
        ref=int(ref); body=p.objs.get(ref,b'')
        if b'/Form' not in body[:300]: continue
        fres=p.dict_inline_or_ref(body,b'Resources')
        p.objs[10**7]=b'/Contents %d 0 R'%ref
        items=sorted(page_items(p,10**7,fres),key=lambda it:(-it[1],it[0]))
        print(f'=== page {i} form {name.decode()}')
        rows=[]
        for x,y,t in items:
            if rows and abs(rows[-1][0]-y)<=ytol: rows[-1][1].append((x,t))
            else: rows.append([y,[(x,t)]])
        for r in rows: print('\t'.join(t for _,t in sorted(r[1])))
