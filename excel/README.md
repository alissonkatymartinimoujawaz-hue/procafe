# Grafico de producao Arabica x Robusta (Excel)

`producao_arabica_robusta.xlsx` reproduz, em Excel nativo, o grafico de barras
com o ciclo bienal ON/OFF do cafe brasileiro:

| Elemento do grafico original | Como foi feito na planilha |
|---|---|
| Barras azuis `Arabica Production` | serie de colunas agrupadas (coluna B) |
| Barras laranja `Robusta Production` | serie de colunas agrupadas (coluna C) |
| Linha preta `Biennial ON/OFF pattern` | coluna E, `=IF(D="ON";nivel_ON;nivel_OFF)` |
| Linha laranja pontilhada `Robusta progression` | coluna F, reta de minimos quadrados (`SLOPE`/`INTERCEPT`) |
| Rotulos `ON` / `OFF` acima das barras | serie invisivel (coluna G) com rotulo formatado por ponto |
| Eixos `Market Year` / `Production (1,000 bags)` | titulos dos eixos, escala 0-62.000, passo 10.000 |

## Como editar

* Celulas amarelas em `K2:K4` (aba **Producao**) sao as premissas do grafico:
  nivel da linha preta em anos ON e OFF e o deslocamento vertical dos rotulos.
* Producao de Arabica (coluna B), de Robusta (coluna C) e o ciclo (coluna D,
  texto `ON`/`OFF`) sao os dados de entrada; as colunas E, F e G recalculam sozinhas.
* Para incluir novos anos-safra, insira linhas antes da ultima e estenda os
  intervalos das series do grafico.

Os valores de producao foram digitalizados do grafico enviado pelo usuario
(mil sacas de 60 kg) — nao vieram de uma base oficial. Substitua-os pelos dados
do USDA/CONAB quando quiser numeros auditaveis.

## Regerar

```bash
python excel/build_production_chart.py
./excel/render_preview.sh excel/producao_arabica_robusta.xlsx /tmp   # confere em PDF
```
