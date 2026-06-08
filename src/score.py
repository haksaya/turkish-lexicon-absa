"""
Sentiment scoring script — Turkish school reviews
Reproduces the lexicon-based scoring pipeline from the paper.

Lexicons:
  STN   : SentiTurkNet  (Turkish stems → sözlükler/sentiturknet.xlsx)
  SWN-EN: SentiWordNet  (English words → sözlükler/sentiwordnet.csv)
  SWN-TR: Not available (was stored in MySQL; cannot be reproduced here)

Input columns used from the review CSV:
  col 3  (durum)    : true label  (p / n)
  col 6  (eksiz_tr) : Turkish stems, space-separated
  col 7  (eksiz_en) : English words, comma-separated
"""

import os
import csv
import openpyxl
import xlrd

BASE          = os.path.join(os.path.dirname(__file__), '..')
STN_PATH      = os.path.join(BASE, 'sözlükler', 'sentiturknet.xlsx')
SWN_PATH      = os.path.join(BASE, 'sözlükler', 'sentiwordnet.csv')
SWN_TR_PATH   = os.path.join(BASE, 'sözlükler', 'sentiwordnet-tr.csv')
XLS_PATH      = os.path.join(BASE, 'yorumlar.xls')
DATA_PATH     = os.path.join(BASE, 'data', 'sample_reviews_data.csv')
RESULT_DIR    = os.path.join(BASE, 'result')
OUT_PATH      = os.path.join(RESULT_DIR, 'results.csv')


# ── Lexicon loaders ─────────────────────────────────────────────────────────

def load_stn(path):
    """
    SentiTurkNet: columns → synonyms(0), neg(4), pos(6).
    First occurrence of each word is kept (TOP-1 behaviour).
    Returns dict: lowercase_word -> (pos_score, neg_score)
    """
    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb.active
    lex = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        word = row[0]
        if not word:
            continue
        key = str(word).strip().lower()
        if key not in lex:
            neg = float(row[4]) if row[4] is not None else 0.0
            pos = float(row[6]) if row[6] is not None else 0.0
            lex[key] = (pos, neg)
    return lex


def load_swn(path):
    """
    SentiWordNet CSV — semicolon-separated:
      POS ; SynsetID ; PosScore ; NegScore ; word#sense ... ; gloss
    First occurrence of each word (stripped of #sense) is kept.
    Returns dict: lowercase_word -> (pos_score, neg_score)
    """
    lex = {}
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(';')
            if len(parts) < 5:
                continue
            try:
                pos_score = float(parts[2])
                neg_score = float(parts[3])
            except ValueError:
                continue
            for term in parts[4].split():
                word = term.split('#')[0].lower().strip()
                if word and word not in lex:
                    lex[word] = (pos_score, neg_score)
    return lex


def load_swn_tr(path):
    """
    SentiWordNet-TR: columns → turkish_word(0), english_word(1), pos(2), neg(3).
    Returns dict: lowercase_turkish_word -> (pos_score, neg_score)
    """
    lex = {}
    with open(path, encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) < 4:
                continue
            word = row[0].strip().lower()
            if not word or word in lex:
                continue
            try:
                pos = float(row[2])
                neg = float(row[3])
            except ValueError:
                continue
            lex[word] = (pos, neg)
    return lex


# ── Scorer ───────────────────────────────────────────────────────────────────

def predict(word_list, lexicon):
    """
    Average pos/neg scores across matched words.
    Predicts 'p' if avg_pos > avg_neg, else 'n'.
    When no word matches (avg_pos == avg_neg == 0), defaults to 'n'.
    """
    pos_sum = neg_sum = 0.0
    count = 0
    for w in word_list:
        key = w.strip().lower()
        if key and key in lexicon:
            p, n = lexicon[key]
            pos_sum += p
            neg_sum += n
            count += 1
    if count == 0:
        return 'n'
    return 'p' if (pos_sum / count) > (neg_sum / count) else 'n'


# ── Metrics ──────────────────────────────────────────────────────────────────

def metrics(true_labels, pred_labels):
    tp = sum(t == 'p' and p == 'p' for t, p in zip(true_labels, pred_labels))
    tn = sum(t == 'n' and p == 'n' for t, p in zip(true_labels, pred_labels))
    fp = sum(t == 'n' and p == 'p' for t, p in zip(true_labels, pred_labels))
    fn = sum(t == 'p' and p == 'n' for t, p in zip(true_labels, pred_labels))
    total = tp + tn + fp + fn

    acc     = (tp + tn) / total if total else 0

    prec_p  = tp / (tp + fp)   if (tp + fp)   else 0
    rec_p   = tp / (tp + fn)   if (tp + fn)   else 0
    f1_p    = 2 * prec_p * rec_p / (prec_p + rec_p) if (prec_p + rec_p) else 0

    prec_n  = tn / (tn + fn)   if (tn + fn)   else 0
    rec_n   = tn / (tn + fp)   if (tn + fp)   else 0
    f1_n    = 2 * prec_n * rec_n / (prec_n + rec_n) if (prec_n + rec_n) else 0

    n_pos   = tp + fn
    n_neg   = tn + fp
    w_f1    = (f1_p * n_pos + f1_n * n_neg) / total if total else 0

    return dict(
        tp=tp, tn=tn, fp=fp, fn=fn, total=total,
        acc=acc,
        prec_p=prec_p, rec_p=rec_p, f1_p=f1_p,
        prec_n=prec_n, rec_n=rec_n, f1_n=f1_n,
        weighted_f1=w_f1,
        n_pos=n_pos, n_neg=n_neg,
    )


def print_metrics(name, m):
    w = 50
    print(f"\n{'=' * w}")
    print(f" {name}")
    print(f"{'=' * w}")
    print(f" Samples : {m['total']}  (pos={m['n_pos']}, neg={m['n_neg']})")
    print(f" TP={m['tp']}  TN={m['tn']}  FP={m['fp']}  FN={m['fn']}")
    print(f" Accuracy: {m['acc']:.4f}  ({m['acc']*100:.2f}%)")
    print(f"\n {'Class':<12} {'Precision':>10} {'Recall':>10} {'F1':>10}")
    print(f" {'-'*44}")
    print(f" {'Positive':<12} {m['prec_p']:>10.4f} {m['rec_p']:>10.4f} {m['f1_p']:>10.4f}")
    print(f" {'Negative':<12} {m['prec_n']:>10.4f} {m['rec_n']:>10.4f} {m['f1_n']:>10.4f}")
    print(f" {'Weighted avg':<12} {'':>10} {'':>10} {m['weighted_f1']:>10.4f}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(RESULT_DIR, exist_ok=True)

    print("Loading lexicons ...")
    stn    = load_stn(STN_PATH)
    print(f"  STN      : {len(stn):,} unique terms")
    swn    = load_swn(SWN_PATH)
    print(f"  SWN-EN   : {len(swn):,} unique terms")
    swn_tr = load_swn_tr(SWN_TR_PATH)
    print(f"  SWN-TR   : {len(swn_tr):,} unique terms")

    print("\nLoading reviews ...")
    with open(DATA_PATH, encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader)
        rows = list(reader)

    # CSV: agay_id(0) yorum_id(1) aspect(2) durum(3)
    #   yorum_metin(4) iliskili(5) eksiz_tr(6) eksiz_en(7)
    true_labels, words_tr, words_en = [], [], []

    for row in rows:
        if len(row) < 8:
            continue
        durum  = row[3].strip().lower()
        tr_raw = row[6].strip()
        en_raw = row[7].strip()
        if durum not in ('p', 'n'):
            continue
        true_labels.append(durum)
        words_tr.append([w for w in tr_raw.split()    if w.strip()])
        words_en.append([w for w in en_raw.split(',') if w.strip()])

    print(f"  Records  : {len(true_labels)}  "
          f"(pos={true_labels.count('p')}, neg={true_labels.count('n')})")

    # ── Score ──
    pred_stn    = [predict(w, stn)    for w in words_tr]
    pred_swn_en = [predict(w, swn)    for w in words_en]
    pred_swn_tr = [predict(w, swn_tr) for w in words_tr]   # TR stems -> SWN-TR

    m_stn    = metrics(true_labels, pred_stn)
    m_swn_en = metrics(true_labels, pred_swn_en)
    m_swn_tr = metrics(true_labels, pred_swn_tr)

    print_metrics('SentiTurkNet       (STN)',    m_stn)
    print_metrics('SentiWordNet-TR    (SWN-TR)', m_swn_tr)
    print_metrics('SentiWordNet-EN    (SWN-EN)', m_swn_en)

    # ── Save CSV ──
    def fmt(v): return round(v, 4) if isinstance(v, float) else v

    rows = [
        ['Lexicon', 'Class', 'Precision', 'Recall', 'F1', 'Support'],
        ['SentiTurkNet',    'Positive', fmt(m_stn['prec_p']),    fmt(m_stn['rec_p']),    fmt(m_stn['f1_p']),           m_stn['n_pos']],
        ['SentiTurkNet',    'Negative', fmt(m_stn['prec_n']),    fmt(m_stn['rec_n']),    fmt(m_stn['f1_n']),           m_stn['n_neg']],
        ['SentiTurkNet',    'Accuracy', '',                       '',                     fmt(m_stn['acc']),            m_stn['total']],
        ['SentiTurkNet',    'Wtd avg',  '',                       '',                     fmt(m_stn['weighted_f1']),    m_stn['total']],
        [],
        ['SentiWordNet-TR', 'Positive', fmt(m_swn_tr['prec_p']), fmt(m_swn_tr['rec_p']), fmt(m_swn_tr['f1_p']),       m_swn_tr['n_pos']],
        ['SentiWordNet-TR', 'Negative', fmt(m_swn_tr['prec_n']), fmt(m_swn_tr['rec_n']), fmt(m_swn_tr['f1_n']),       m_swn_tr['n_neg']],
        ['SentiWordNet-TR', 'Accuracy', '',                       '',                     fmt(m_swn_tr['acc']),         m_swn_tr['total']],
        ['SentiWordNet-TR', 'Wtd avg',  '',                       '',                     fmt(m_swn_tr['weighted_f1']), m_swn_tr['total']],
        [],
        ['SentiWordNet-EN', 'Positive', fmt(m_swn_en['prec_p']), fmt(m_swn_en['rec_p']), fmt(m_swn_en['f1_p']),       m_swn_en['n_pos']],
        ['SentiWordNet-EN', 'Negative', fmt(m_swn_en['prec_n']), fmt(m_swn_en['rec_n']), fmt(m_swn_en['f1_n']),       m_swn_en['n_neg']],
        ['SentiWordNet-EN', 'Accuracy', '',                       '',                     fmt(m_swn_en['acc']),         m_swn_en['total']],
        ['SentiWordNet-EN', 'Wtd avg',  '',                       '',                     fmt(m_swn_en['weighted_f1']), m_swn_en['total']],
    ]

    with open(OUT_PATH, 'w', newline='', encoding='utf-8-sig') as f:
        csv.writer(f).writerows(rows)
    print(f"\nResults saved -> {OUT_PATH}")


if __name__ == '__main__':
    main()
