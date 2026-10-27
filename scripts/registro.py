"""Aplica ao data/lotes.json o desmembramento REGISTRADO (34 glebas, matrículas 15.195–15.228).
A planta fracionada (57 glebas) continua em `glebas_planta` (usada pelas avenidas e pelos selos do desenho);
`glebas` passa a ser a divisão do cartório e cada lote recebe `gleba` (registrada), `matricula` e `gleba_planta`.
Fonte: data/registro_34.json (gerado da análise em planejamento-estrategico/00-insumos/glebas/).
Também aplica ajustes de status informados pela administração e ainda não lançados na Planilha Mestre.
Uso: python scripts/registro.py  (chamado no fim de gerar_dados.py)"""
import json, os
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.abspath(os.path.join(HERE, ".."))
ARQ = os.path.join(RAIZ, "data", "lotes.json"); REG = json.load(open(os.path.join(RAIZ, "data", "registro_34.json"), encoding="utf-8"))
# status informado pelo Jachson e ainda não lançado na Planilha Mestre (remover quando a planilha for atualizada)
STATUS_AJUSTE = {"110": "vendido"}   # 27/10/2026: lote 110 vendido
J = json.load(open(ARQ, encoding="utf-8"))
if "glebas_planta" not in J: J["glebas_planta"] = J["glebas"]
J["selos"] = [g["label"] for g in J["glebas_planta"] if isinstance(g.get("label"), list)]
def centro(P):
    a = cx = cy = 0
    for i in range(len(P)):
        x1, y1 = P[i-1]; x2, y2 = P[i]; c = x1*y2 - x2*y1; a += c; cx += (x1+x2)*c; cy += (y1+y2)*c
    return [round(cx/(3*a), 2), round(cy/(3*a), 2)]
J["glebas"] = [{"id": g["id"], "matricula": g["matricula"], "area_ha": g["area_ha"], "poly": g["poly"], "label": centro(g["poly"])} for g in REG["glebas"]]
gp = {l: g["id"] for g in J["glebas_planta"] for l in g.get("lotes", [])}
for l in J["lotes"]:
    r = REG["lotes"].get(l["id"])
    l["gleba_planta"] = gp.get(l["id"], l.get("gleba_planta", l.get("gleba")))
    if r: l["gleba"] = r["gleba"]; l["matricula"] = r["matricula"]
    if l["id"] in STATUS_AJUSTE: l["status"] = STATUS_AJUSTE[l["id"]]
c = Counter(l["status"] for l in J["lotes"])
J["meta"].update({"glebas": len(J["glebas"]), "glebas_planta": len(J["glebas_planta"]), "registro": REG["fonte"],
                  "disponiveis": c["disponivel"], "vendidos": c["vendido"], "reservados": c["reservado"], "reserva_tecnica": c["reserva_tecnica"]})
json.dump(J, open(ARQ, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("registro aplicado: 34 glebas registradas |", dict(c))
