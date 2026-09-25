import zipfile,re,sys,glob
for f in sorted(glob.glob('*.xlsx')):
    try:
        z=zipfile.ZipFile(f); wb=z.read('xl/workbook.xml').decode('utf8','ignore')
        names=re.findall(r'<sheet [^>]*name="([^"]+)"',wb)
        ss=z.read('xl/sharedStrings.xml').decode('utf8','ignore') if 'xl/sharedStrings.xml' in z.namelist() else ''
        strs=re.findall(r'<t[^>]*>([^<]*)</t>',ss)
        hits=[s for s in strs if re.search(r'caf[eé]|agropec|agricult|actividad',s,re.I)][:8]
        print(f'{f} | sheets: {"; ".join(names)} | strings mentioning cafe/agro/actividad: {hits}')
    except Exception as e: print(f,'ERR',e)
