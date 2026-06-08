# A Novel Lexicon-Based Approach for Sentiment Analysis in Turkish

[![GitHub](https://img.shields.io/badge/GitHub-haksaya%2Fturkish--lexicon--absa-blue)](https://github.com/haksaya/turkish-lexicon-absa)

Supplementary code and data for the paper submitted to MDPI Applied Sciences.

**Authors:** Harun Aksaya, Sevinç Gülseçen  
**Affiliation:** Marmara University / Istanbul University  
**Repository:** https://github.com/haksaya/turkish-lexicon-absa

---

## Overview

This repository provides the scoring scripts, sample dataset, and result files for the
lexicon-based aspect-level sentiment analysis study on Turkish school reviews.

Three lexicon configurations are compared:
- **SentiTurkNet** (native Turkish lexicon)
- **SentiWordNet-TR** (machine-translated English lexicon)
- **SentiWordNet-EN** (original English lexicon with target-term translation)

---

## Repository Structure

```
├── src/
│   └── score.py              # Main scoring & evaluation script
├── data/
│   └── sample_reviews_data.csv    #sample data set (full dataset available on request)
├── lexicons/
│   └── README.md             # Lexicon download instructions and licence information
├── results/
│   └── results.csv           # Precision / Recall / F1 per class for each lexicon
└── requirements.txt
```

---

## Requirements

```bash
pip install -r requirements.txt
```

Python 3.8+ recommended.

---

## Usage

### 1. Download lexicons
Follow the instructions in `lexicons/README.md` to download and place the lexicon files.

### 2. Prepare the dataset
Place your review CSV at `data/sample_reviews_data.csv` (see column format in the sample file).

### 3. Run scoring

```bash
python src/score.py
```

Results are saved to `results/results.csv` and printed to the console.

---

## Dataset

The full annotated dataset (1,925 aspect-level targets from 1,000 Turkish school reviews)
is available upon request from the corresponding author: harunaksaya@marmara.edu.tr

The dataset was collected from okul.com.tr under a data-sharing agreement.
All reviews are anonymised.

---

## Citation

If you use this code or data, please cite:

```
Aksaya, H.; Gülseçen, S. A Novel Lexicon-Based Approach for Sentiment Analysis in Turkish.
Applied Sciences, 2025. (under review)
```

---

## Licence

Code: MIT License
Data sample: for research use only
Lexicons: see `lexicons/README.md`
