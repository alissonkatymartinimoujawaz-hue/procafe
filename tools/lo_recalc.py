#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recalculate an .xlsx with LibreOffice so every formula carries its value (openpyxl
writes formulas without results), fail on any formula error, and export the charts
of the 'Charts' sheet as PNG previews.
Runs with the system Python that has LibreOffice's `uno` module:
    /usr/bin/python3 tools/lo_recalc.py exports/file.xlsx exports/preview
"""
import os, subprocess, sys, tempfile, time

import uno
from com.sun.star.beans import PropertyValue


def pv(name, value):
    p = PropertyValue()
    p.Name, p.Value = name, value
    return p


def main(path, png_dir=None):
    profile = tempfile.mkdtemp(prefix="lo_profile_")
    proc = subprocess.Popen(["soffice", "--headless", "--invisible", "--nologo", "--norestore",
                             f"-env:UserInstallation=file://{profile}",
                             "--accept=socket,host=127.0.0.1,port=2083;urp;"],
                            env=dict(os.environ, SAL_USE_VCLPLUGIN="svp"),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
    for _ in range(120):
        try:
            ctx = resolver.resolve("uno:socket,host=127.0.0.1,port=2083;urp;StarOffice.ComponentContext")
            break
        except Exception:
            time.sleep(0.5)
    else:
        sys.exit("LibreOffice did not start")
    smgr = ctx.ServiceManager
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    url = uno.systemPathToFileUrl(os.path.abspath(path))
    doc = desktop.loadComponentFromURL(url, "_blank", 0, (pv("Hidden", True),))
    doc.calculateAll()
    formulas, errors = 0, []
    for sheet in doc.Sheets:
        cur = sheet.createCursor()
        cur.gotoEndOfUsedArea(False)
        for r in range(cur.RangeAddress.EndRow + 1):
            for c in range(cur.RangeAddress.EndColumn + 1):
                cell = sheet.getCellByPosition(c, r)
                if cell.getFormula().startswith("="):
                    formulas += 1
                    if cell.getError():
                        errors.append(f"{sheet.Name}!{cell.AbsoluteName.split('.')[-1]} {cell.getFormula()}")
    print(f"formulas: {formulas}, errors: {len(errors)}")
    for e in errors[:50]:
        print("  ERROR", e)
    doc.storeToURL(url, (pv("FilterName", "Calc MS Excel 2007 XML"),))
    if png_dir and doc.Sheets.hasByName("Charts"):
        os.makedirs(png_dir, exist_ok=True)
        page = doc.Sheets.getByName("Charts").DrawPage
        gef = smgr.createInstanceWithContext("com.sun.star.drawing.GraphicExportFilter", ctx)
        for i in range(page.Count):
            gef.setSourceDocument(page.getByIndex(i))
            gef.filter((pv("URL", uno.systemPathToFileUrl(os.path.abspath(os.path.join(png_dir, f"excel_chart_{i:02d}.png")))),
                        pv("MediaType", "image/png"),
                        pv("FilterData", (pv("PixelWidth", 900), pv("PixelHeight", 480)))))
        print("chart previews:", page.Count)
    doc.close(True)
    try:
        desktop.terminate()
    except Exception:
        pass
    proc.wait(timeout=60)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main(*sys.argv[1:3])
