def winrate(a, b, c, d):
    return a*c + b*d + (a*d + b*c)/2 - (a*b*c + a*b*d + a*c*d + b*c*d)/2

for a in [0, 0.5, 1]:
    for b in [0, 0.5, 1]:
        for c in [0, 0.5, 1]:
            for d in [0, 0.5, 1]:
                wr = winrate(a, b, c, d)
                if (wr >= 0.5):
                    print("a =", a, "b =", b, "c =", c, "d =", d, "wr =", wr)