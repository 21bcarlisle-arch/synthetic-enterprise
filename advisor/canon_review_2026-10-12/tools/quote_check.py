"""Check every quoted span in the reconciled canon documents against the source corpus.

Usage: python3 -I quote_check.py <corpus_root> <corpus_paths.txt> <extra_file>... -- <doc>...
Prints per-document hit rates and writes a JSON report of misses and where each hit was found.
"""
import re, sys, json, os, unicodedata

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    s = s.replace("—", "-").replace("–", "-").replace("−", "-")
    s = re.sub(r"[*_`>#|]", " ", s)
    s = s.lower()
    s = re.sub(r"\\n", " ", s)
    s = s.replace("'", "").replace('"', "")
    s = re.sub(r"[^a-z0-9£%.,;:!?()\-/= +]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r" ([.,;:!?)])", r"\1", s)
    s = re.sub(r"\( ", "(", s)
    return s

def fragments(q):
    parts = re.split(r"\.\.\.|…|\[[^\]]*\]", q)
    out = []
    for p in parts:
        p = norm(p).strip(" .,;:!?-'\"")
        if len(p.split()) >= 4:
            out.append(p)
    return out

args = sys.argv[1:]
sep = args.index("--")
root, listfile, extras, docs = args[0], args[1], args[2:sep], args[sep + 1:]
corpus = {}
for rel in open(listfile).read().split():
    p = os.path.join(root, rel)
    if os.path.exists(p):
        corpus[rel] = norm(open(p, errors="replace").read())
for e in extras:
    corpus[os.path.basename(e)] = norm(open(e, errors="replace").read())

quote_re = re.compile(r'"([^"\n]{12,}?)"|“([^”\n]{12,}?)”')
report = {}
for d in docs:
    txt = open(d).read()
    qs = [m.group(1) or m.group(2) for m in quote_re.finditer(txt)]
    hits, misses, checked = [], [], 0
    for q in qs:
        fr = fragments(q)
        if not fr:
            continue
        checked += 1
        where = []
        ok = True
        for f in fr:
            found = next((k for k, v in corpus.items() if f in v), None)
            if found is None:
                ok = False
                break
            where.append(found)
        (hits if ok else misses).append({"quote": q[:220], "found_in": sorted(set(where))})
    report[os.path.basename(d)] = {"checked": checked, "found": len(hits), "missed": misses, "hits": hits}
    print(f"{os.path.basename(d):45s} quotes checked {checked:4d}  found {len(hits):4d}  missed {len(misses):3d}")
tot_c = sum(r["checked"] for r in report.values()); tot_f = sum(r["found"] for r in report.values())
print(f"TOTAL checked {tot_c} found {tot_f} ({100*tot_f/max(tot_c,1):.1f}%)")
json.dump(report, open(os.environ.get("QC_OUT", "quote_check_report.json"), "w"), indent=1)
