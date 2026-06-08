# Lexicons

This folder contains information about the sentiment lexicons used in the study.
The lexicon files themselves are **not distributed** in this repository due to licence constraints.
Please download them from the official sources below.

---

## SentiWordNet

- **Source:** https://github.com/aesuli/SentiWordNet
- **Format:** semicolon-separated CSV (`POS;SynsetID;PosScore;NegScore;SynsetTerms;Gloss`)
- **Size:** 117,659 entries
- **Licence:** Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
- **Citation:** Baccianella, S.; Esuli, A.; Sebastiani, F. SentiWordNet 3.0. LREC 2010.

After downloading, place the file at: `lexicons/sentiwordnet.csv`

---

## SentiTurkNet

SentiTurkNet can be downloaded from the authors' page (see source link below).

- **Source:** https://myweb.sabanciuniv.edu/rdehkharghani/sentiturknet-3/
- **Format:** Excel (.xlsx) — columns: synonyms, Turkish Gloss, Polarity Label, POS tag, neg value, obj value, pos value, Eng Synonyms, English Gloss, SWNpos, SWNneg
- **Size:** 14,795 entries
- **Licence:** Academic use; no explicit open data licence. Contact the authors for commercial use.

After downloading, place the file at: `lexicons/sentiturknet.xlsx`

**Citation:**

```bibtex
@article{dehkharghani2015sentiturknet,
  title   = {SentiTurkNet: a Turkish polarity lexicon for sentiment analysis},
  author  = {Dehkharghani, Rahim and Saygin, Yucel and Yanikoglu, Berrin and Oflazer, Kemal},
  journal = {Language Resources and Evaluation},
  pages   = {1--19},
  year    = {2016},
  publisher = {Springer}
}
