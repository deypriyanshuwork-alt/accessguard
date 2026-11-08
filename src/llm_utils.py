import json, time, os
import pandas as pd, ollama
from tqdm import tqdm
from sklearn.metrics import precision_score, recall_score, f1_score

TYPES = ["NONE", "SOD_CREATE_PAY", "SELF_APPROVAL", "VENDOR_CREATE_PAY",
         "MISSING_APPROVAL", "SPLIT_BELOW_THRESHOLD"]

SCHEMA = {"type": "object",
          "properties": {"reason": {"type": "string"},
                         "violation": {"type": "boolean"},
                         "violation_type": {"type": "string", "enum": TYPES}},
          "required": ["reason", "violation", "violation_type"]}

def ask(model, messages):
    t0 = time.time()
    r = ollama.chat(model=model, messages=messages, format=SCHEMA,
                    options={"temperature": 0, "seed": 42, "num_predict": 200, "num_ctx": 4096},
                    keep_alive="30m")
    wall = time.time() - t0
    txt = r["message"]["content"]
    try:
        o = json.loads(txt)
        return dict(pred_violation=bool(o["violation"]), pred_type=o["violation_type"],
                    reason=o["reason"], valid_json=True, sec=wall)
    except Exception:
        return dict(pred_violation=False, pred_type="INVALID", reason=txt[:200],
                    valid_json=False, sec=wall)

def unload(model):
    ollama.generate(model=model, prompt="", keep_alive=0)

def binary_metrics(y_true, y_pred):
    return dict(precision=precision_score(y_true, y_pred, zero_division=0),
                recall=recall_score(y_true, y_pred, zero_division=0),
                f1=f1_score(y_true, y_pred, zero_division=0))

def run_eval(model, build, df, tag):
    """build: function(summary) -> list of chat messages. Resumes if interrupted."""
    path = f"../results/{tag}.csv"
    rows = pd.read_csv(path).to_dict("records") if os.path.exists(path) else []
    done = {r["po_number"] for r in rows}
    for r in tqdm(df.itertuples(), total=len(df)):
        if r.po_number in done:
            continue
        out = ask(model, build(r.summary))
        rows.append(dict(po_number=r.po_number, true_label=r.label, true_type=r.violation_type, **out))
        if len(rows) % 25 == 0:
            pd.DataFrame(rows).to_csv(path, index=False)
    res = pd.DataFrame(rows); res.to_csv(path, index=False)
    return res

def evaluate(res, name):
    y_t = (res.true_label == "violation").astype(int)
    y_p = res.pred_violation.astype(int)
    m = binary_metrics(y_t, y_p)
    v = res[res.true_label == "violation"]
    m.update(type_acc_on_violations=(v.pred_type == v.true_type).mean(),
             invalid_json=1 - res.valid_json.mean(), sec_per_case=res.sec.mean(),
             n=len(res), name=name)
    return m