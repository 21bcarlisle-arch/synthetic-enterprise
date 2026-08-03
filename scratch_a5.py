import json
cap = json.load(open("docs/market_research/w1_7_dukes_installed_capacity_annual.json"))
gen = json.load(open("docs/market_research/w1_7_dukes_generation_and_load_factor_annual.json"))
H = {2016: 8784, 2017: 8760, 2018: 8760, 2019: 8760, 2020: 8784,
     2021: 8760, 2022: 8760, 2023: 8760, 2024: 8784, 2025: 8760}
capkey = {"onshore_wind": "onshore_mw", "offshore_wind": "offshore_mw", "solar": "solar_mw"}
print(f"{'tech':14s}{'yr':>6}{'end_err%':>10}{'mean_err%':>10}")
tot_end = []
tot_mean = []
for t, ck in capkey.items():
    s = cap[ck]
    yrs = sorted(int(y) for y in s)
    for y in yrs:
        real = gen["generation_gwh"][t].get(str(y))
        lf = gen["load_factor_pct"][t].get(str(y))
        if real is None or lf is None:
            continue
        real = float(real)
        lf = float(lf) / 100
        c_end = float(s[str(y)])
        c_prev = float(s[str(y - 1)]) if str(y - 1) in s else None
        imp_end = c_end * lf * H[y] / 1000
        e1 = (imp_end - real) / real * 100
        if c_prev is None:
            print(f"{t:14s}{y:>6}{e1:>10.1f}{'n/a':>10}")
            tot_end.append(abs(e1))
            continue
        c_mean = (c_prev + c_end) / 2
        imp_mean = c_mean * lf * H[y] / 1000
        e2 = (imp_mean - real) / real * 100
        print(f"{t:14s}{y:>6}{e1:>10.1f}{e2:>10.1f}")
        tot_end.append(abs(e1))
        tot_mean.append(abs(e2))
print()
print(f"year-END  : max|e|={max(tot_end):.1f}% mean|e|={sum(tot_end)/len(tot_end):.1f}% n={len(tot_end)}")
print(f"year-MEAN : max|e|={max(tot_mean):.1f}% mean|e|={sum(tot_mean)/len(tot_mean):.1f}% n={len(tot_mean)}")
