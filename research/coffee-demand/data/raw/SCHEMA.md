# Raw data schema (every research CSV uses exactly these columns)

dataset,entity,period,value,unit,source_org,source_title,source_url,quote,confidence,notes

- dataset    : short machine name, e.g. world_consumption_usda, price_annual_ico_composite
- entity     : country / region / company / price series, e.g. "World", "European Union", "Brazil", "Starbucks"
- period     : marketing year "2015/16", coffee year "CY2015/16", calendar year "2015", month "2015-03"
- value      : number only (no thousands separators), blank if not found
- unit       : e.g. "million 60kg bags", "1000 60kg bags", "US cents/lb", "USD/kg", "stores", "%"
- source_org : USDA FAS, ICO, World Bank, IMF, Eurostat, ABIC, NCA, company name, ...
- source_title : report/page title (e.g. "Coffee: World Markets and Trade, June 2026")
- source_url : URL of the page the number came from (from the search result)
- quote      : short verbatim snippet containing the number (<= 200 chars), use double quotes escaped per CSV rules
- confidence : high (official source, explicit number) | medium (reputable press quoting official source) | low (indirect / conflicting)
- notes      : vintage (report date), revisions, definitional caveats
