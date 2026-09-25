"""Independent check of an .xlsx written by xlsxw.py: re-reads the file, recomputes every formula with a small evaluator
(the functions used in the workbook) and compares with the cached value stored in the file. Standard library only.
Usage: python3 verify_xlsx.py file.xlsx"""
import sys, re, zipfile, math, fnmatch, datetime, decimal
import xml.etree.ElementTree as ET

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
path = sys.argv[1]
z = zipfile.ZipFile(path)
wbx = ET.fromstring(z.read('xl/workbook.xml'))
rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
SHEETS = {}
for s in wbx.iter(NS + 'sheet'):
    rid = s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
    SHEETS[s.get('name')] = 'xl/' + rels[rid]


def col_num(s):
    n = 0
    for ch in s:
        n = n * 26 + ord(ch) - 64
    return n


CELLS = {}   # sheet -> {(r,c): (cached, formula)}
MAXR = {}
for name, part in SHEETS.items():
    d = {}
    mr = 0
    for c in ET.fromstring(z.read(part)).iter(NS + 'c'):
        m = re.match(r'([A-Z]+)(\d+)', c.get('r'))
        rc = (int(m.group(2)), col_num(m.group(1)))
        mr = max(mr, rc[0])
        t = c.get('t')
        f = c.find(NS + 'f')
        v = c.find(NS + 'v')
        if t == 'inlineStr':
            val = ''.join(x.text or '' for x in c.iter(NS + 't'))
        elif v is None or v.text is None:
            val = None if t != 'str' else ''
        elif t in ('str', 's'):
            val = v.text
        elif t == 'b':
            val = v.text == '1'
        else:
            val = float(v.text)
        d[rc] = (val, f.text if f is not None else None)
    CELLS[name] = d
    MAXR[name] = mr

# ---------------- tokenizer / parser ----------------
TOK = re.compile(r'\s*(?:(?P<str>"(?:[^"]|"")*")|(?P<ref>(?:[A-Za-z_][A-Za-z0-9_]*!)?\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?|(?:[A-Za-z_][A-Za-z0-9_]*!)?\$?[A-Z]{1,3}:\$?[A-Z]{1,3})(?![A-Za-z0-9_(])'
                 r'|(?P<func>[A-Z][A-Z0-9.]*)\(|(?P<num>\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)|(?P<op><>|>=|<=|[-+*/&=<>(),]))')


def tokenize(s):
    out, i = [], 0
    while i < len(s):
        m = TOK.match(s, i)
        if not m or m.end() == i:
            if s[i:].strip() == '':
                break
            raise ValueError('cannot parse %r at %d' % (s, i))
        i = m.end()
        k = m.lastgroup
        out.append((k, m.group(k)))
    return out


class P:
    def __init__(self, toks):
        self.t, self.i = toks, 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def take(self):
        self.i += 1
        return self.t[self.i - 1]

    def expr(self):  # comparison
        a = self.concat()
        while self.peek()[0] == 'op' and self.peek()[1] in ('=', '<>', '<', '>', '<=', '>='):
            op = self.take()[1]
            a = ('cmp', op, a, self.concat())
        return a

    def concat(self):
        a = self.add()
        while self.peek() == ('op', '&'):
            self.take()
            a = ('cat', a, self.add())
        return a

    def add(self):
        a = self.mul()
        while self.peek()[0] == 'op' and self.peek()[1] in '+-' and len(self.peek()[1]) == 1:
            op = self.take()[1]
            a = ('bin', op, a, self.mul())
        return a

    def mul(self):
        a = self.unary()
        while self.peek()[0] == 'op' and self.peek()[1] in ('*', '/'):
            op = self.take()[1]
            a = ('bin', op, a, self.unary())
        return a

    def unary(self):
        if self.peek() == ('op', '-'):
            self.take()
            return ('neg', self.unary())
        return self.atom()

    def atom(self):
        k, v = self.take()
        if k == 'num':
            return ('num', float(v))
        if k == 'str':
            return ('str', v[1:-1].replace('""', '"'))
        if k == 'ref':
            return ('ref', v)
        if k == 'func':
            args = []
            if self.peek() != ('op', ')'):
                args.append(self.expr())
                while self.peek() == ('op', ','):
                    self.take()
                    args.append(self.expr())
            assert self.take() == ('op', ')')
            return ('fn', v, args)
        if (k, v) == ('op', '('):
            e = self.expr()
            assert self.take() == ('op', ')')
            return e
        raise ValueError('unexpected %s %s' % (k, v))


class Rng:
    def __init__(self, sheet, r1, c1, r2, c2):
        self.s, self.r1, self.c1, self.r2, self.c2 = sheet, r1, c1, r2, c2

    def cells(self):
        for r in range(self.r1, self.r2 + 1):
            for c in range(self.c1, self.c2 + 1):
                yield r, c


def parse_ref(ref, cur_sheet):
    sh = cur_sheet
    if '!' in ref:
        sh, ref = ref.split('!')
    ref = ref.replace('$', '')
    m = re.fullmatch(r'([A-Z]+)(\d+)?(?::([A-Z]+)(\d+)?)?', ref)
    c1 = col_num(m.group(1))
    r1 = int(m.group(2)) if m.group(2) else 1
    c2 = col_num(m.group(3)) if m.group(3) else c1
    r2 = int(m.group(4)) if m.group(4) else (MAXR[sh] if not m.group(2) else r1)
    return Rng(sh, r1, c1, r2, c2)


MEMO, BUSY = {}, set()
PARSED = {}


def value(sh, r, c):
    key = (sh, r, c)
    if key in MEMO:
        return MEMO[key]
    cached, f = CELLS[sh].get((r, c), (None, None))
    if f is None:
        v = cached
    else:
        assert key not in BUSY, 'circular %s' % (key,)
        BUSY.add(key)
        if f not in PARSED:
            PARSED[f] = P(tokenize(f)).expr()
        v = ev(PARSED[f], sh, r)
        BUSY.discard(key)
    MEMO[key] = v
    return v


COLCACHE = {}


def rvals(rg):
    k = (rg.s, rg.r1, rg.c1, rg.r2, rg.c2)
    if k not in COLCACHE:
        COLCACHE[k] = [value(rg.s, r, c) for r, c in rg.cells()]
    return COLCACHE[k]


def crit_fn(cr):
    if isinstance(cr, str):
        m = re.match(r'(<>|>=|<=|=|>|<)(.*)', cr)
        if m:
            op, rhs = m.groups()
            try:
                x = float(rhs)
            except ValueError:
                x = rhs
            return lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and cmp(op, v, x) if isinstance(x, float) else cmp(op, str(v).lower(), x.lower())
        if '*' in cr or '?' in cr:
            pat = cr.lower()
            return lambda v: isinstance(v, str) and fnmatch.fnmatchcase(v.lower(), pat)
        return lambda v: isinstance(v, str) and v.lower() == cr.lower()
    return lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and abs(v - cr) < 1e-12


def cmp(op, a, b):
    return {'=': a == b, '<>': a != b, '<': a < b, '>': a > b, '<=': a <= b, '>=': a >= b}[op]


def excel_round(x, n):
    q = decimal.Decimal(1).scaleb(-int(n))
    return float(decimal.Decimal(repr(x)).quantize(q, rounding=decimal.ROUND_HALF_UP))


def nums(args, sh, r):
    out = []
    for a in args:
        v = ev(a, sh, r, keep_range=True)
        if isinstance(v, Rng):
            out += [x for x in rvals(v) if isinstance(x, float) and not isinstance(x, bool)]
        elif isinstance(v, (int, float)):
            out.append(float(v))
    return out


def ev(n, sh, r, keep_range=False):
    k = n[0]
    if k == 'num':
        return n[1]
    if k == 'str':
        return n[1]
    if k == 'ref':
        rg = parse_ref(n[1], sh)
        if keep_range or (rg.r1, rg.c1) != (rg.r2, rg.c2):
            return rg
        return value(rg.s, rg.r1, rg.c1)
    if k == 'neg':
        return -ev(n[1], sh, r)
    if k == 'bin':
        a, b = ev(n[2], sh, r), ev(n[3], sh, r)
        a = 0.0 if a is None else a
        b = 0.0 if b is None else b
        op = n[1]
        return a + b if op == '+' else a - b if op == '-' else a * b if op == '*' else a / b
    if k == 'cat':
        f = lambda x: ('%d' % x if float(x).is_integer() else repr(x)) if isinstance(x, float) else ('' if x is None else str(x))
        return f(ev(n[1], sh, r)) + f(ev(n[2], sh, r))
    if k == 'cmp':
        a, b = ev(n[2], sh, r), ev(n[3], sh, r)
        if isinstance(a, str) and isinstance(b, str):
            a, b = a.lower(), b.lower()
        return cmp(n[1], a, b)
    name, args = n[1], n[2]
    if name == 'IF':
        return ev(args[1], sh, r) if ev(args[0], sh, r) else (ev(args[2], sh, r) if len(args) > 2 else False)
    if name == 'ROUND':
        return excel_round(ev(args[0], sh, r), ev(args[1], sh, r))
    if name == 'ABS':
        return abs(ev(args[0], sh, r))
    if name in ('LN', 'EXP', 'SQRT'):
        return {'LN': math.log, 'EXP': math.exp, 'SQRT': math.sqrt}[name](ev(args[0], sh, r))
    if name == 'CORREL':
        # Excel drops a pair when either cell is empty or text
        a, b = rvals(ev(args[0], sh, r, True)), rvals(ev(args[1], sh, r, True))
        pr = [(x, y) for x, y in zip(a, b) if isinstance(x, float) and isinstance(y, float) and not isinstance(x, bool) and not isinstance(y, bool)]
        mx, my = sum(x for x, _ in pr) / len(pr), sum(y for _, y in pr) / len(pr)
        sxy = sum((x - mx) * (y - my) for x, y in pr)
        return sxy / math.sqrt(sum((x - mx) ** 2 for x, _ in pr) * sum((y - my) ** 2 for _, y in pr))
    if name == 'LEFT':
        return str(ev(args[0], sh, r))[:int(ev(args[1], sh, r))]
    if name == 'ROW':
        return float(r)
    if name == 'DATE':
        y, m, d = (int(ev(a, sh, r)) for a in args)
        return float((datetime.date(y, m, d) - datetime.date(1899, 12, 30)).days)
    if name in ('SUM', 'AVERAGE', 'MAX', 'MIN', 'COUNT'):
        xs = nums(args, sh, r)
        return {'SUM': lambda: sum(xs), 'AVERAGE': lambda: sum(xs) / len(xs), 'MAX': lambda: max(xs), 'MIN': lambda: min(xs), 'COUNT': lambda: float(len(xs))}[name]()
    if name == 'COUNTBLANK':
        return float(sum(1 for x in rvals(ev(args[0], sh, r, True)) if x is None or x == ''))
    if name in ('COUNTIF', 'COUNTIFS', 'SUMIFS', 'AVERAGEIFS'):
        if name in ('SUMIFS', 'AVERAGEIFS'):
            target = rvals(ev(args[0], sh, r, True))
            pairs = args[1:]
        else:
            target = None
            pairs = args
        cols = [(rvals(ev(pairs[i], sh, r, True)), crit_fn(ev(pairs[i + 1], sh, r))) for i in range(0, len(pairs), 2)]
        idx = [j for j in range(len(cols[0][0])) if all(fn(col[j]) for col, fn in cols)]
        if target is None:
            return float(len(idx))
        xs = [target[j] for j in idx if isinstance(target[j], float)]
        return sum(xs) if name == 'SUMIFS' else sum(xs) / len(xs)
    if name == 'MATCH':
        look = ev(args[0], sh, r)
        vals = rvals(ev(args[1], sh, r, True))
        for j, x in enumerate(vals):
            if (isinstance(look, str) and isinstance(x, str) and x.lower() == look.lower()) or (not isinstance(look, str) and x == look):
                return float(j + 1)
        raise LookupError('#N/A MATCH %r' % (look,))
    if name == 'INDEX':
        rg = ev(args[0], sh, r, True)
        i = int(ev(args[1], sh, r))
        j = int(ev(args[2], sh, r)) if len(args) > 2 else 1
        if rg.c1 == rg.c2 and len(args) == 2:
            return value(rg.s, rg.r1 + i - 1, rg.c1)
        return value(rg.s, rg.r1 + i - 1, rg.c1 + j - 1)
    raise NotImplementedError(name)


nf, bad = 0, []
for sh, cells in CELLS.items():
    for (r, c), (cached, f) in cells.items():
        if f is None:
            continue
        nf += 1
        try:
            v = value(sh, r, c)
        except Exception as e:
            bad.append((sh, r, c, f, 'ERROR %s' % e))
            continue
        if isinstance(v, bool) or isinstance(cached, bool):
            ok = bool(v) == bool(cached) if isinstance(cached, bool) else False
        elif isinstance(v, (int, float)) and isinstance(cached, float):
            ok = abs(v - cached) <= 1e-6 * max(1.0, abs(cached))
        else:
            ok = str(v) == str(cached)
        if not ok:
            bad.append((sh, r, c, f, 'computed %r, cached %r' % (v, cached)))
print('formulas checked:', nf, '| mismatches or errors:', len(bad))
for b in bad[:25]:
    print('  ', b)
sys.exit(1 if bad else 0)
