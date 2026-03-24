# Cross-Cultural Parameter Comparison

English data: HumanLLMs/Human-Like-DPO-Dataset (n=10,884)

| 指標 | EN Human-Like | EN Formal | JA Casual |
|------|--------------|----------|---------|
| 文長CV | 0.6340 | 0.4317 | 0.4298 | 
| Hedge/曖昧表現率 | 0.0817 | 0.0174 | 0.0890 | 
| 自己訂正率 | 0.0430 | 0.0009 | 0.0106 | 
| クッション率 | 0.1578 | 0.0187 | 0.0020 | 
| フィラー率 | 0.3340 | 0.1007 | 0.0385 | 

### Japanese-only metrics
| 指標 | JA Casual |
|------|---------|
| 形態素数/文 | 12.3129 |
| 漢字含有率 | 0.2825 |

---

## Analysis

### Universal patterns (base parameter candidates)
- Metrics with similar ratios across EN and JA suggest language-agnostic defaults

### Culture-specific divergence
- Metrics with large EN/JA differences should be reflected in config/ja.json
- Japanese cushion rate is expected to be higher (high-context culture)
- Japanese kanji ratio replaces Flesch for readability assessment