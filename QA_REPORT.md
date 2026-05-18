# QA Report — Sprint Burndown Chart
**Data:** 2026-05-18  
**Versão analisada:** branch `main` (commit `303369e`)  
**Metodologia:** revisão estática do código + análise de fluxos de utilizador + edge cases

---

## Bugs Críticos (crash / perda de dados)

### QA-01 · `renderChart` e `renderReviewChart` — divisão por zero quando `days = 0`
**Fluxo:** Criar sprint com início e fim no mesmo fim de semana → `countBusinessDays` retorna 0 → `total / days` = `Infinity` → linha ideal corrompida com `Infinity/NaN` → Chart.js renderiza gráfico em branco/inválido.  
**Ficheiro:** `index.html` linhas 2197 e 2301  
**Fix conhecido:** `const safeDays = Math.max(days, 1)` (já registado em BUGS.md #1)

---

### QA-02 · `mergeFromCloud` — `TypeError` se `cloudSprint.items` for `undefined`
**Fluxo:** Cloud contém um sprint sem o campo `items` (backup antigo, edição manual via API) → `cloudSprint.items.forEach(...)` crasha → a app deixa de fazer polling/merge.  
**Ficheiro:** `index.html` linha ~1340  
**Fix conhecido:** `(cloudSprint.items || []).forEach(...)` (já registado em BUGS.md #2)

---

## Bugs de Alta Prioridade (perda de estado do utilizador)

### QA-03 · `editingItemId` persiste após mudar de sprint
**Fluxo:** Utilizador clica "Editar" num item do Sprint A → digita novo valor → sem guardar, muda para Sprint B → `editingItemId` continua apontar para o ID do item antigo → ao voltar ao Sprint A o item aparece em modo de edição sem o utilizador ter pedido, e os valores editados estão perdidos (o input mostra o valor guardado, não o que o utilizador digitou).  
**Ficheiro:** `switchSprint()` não faz `editingItemId = null`  
**Fix:** Adicionar `editingItemId = null;` no início de `switchSprint`.

---

### QA-04 · Sem feedback visual quando a gravação na cloud falha
**Fluxo:** Utilizador faz alterações → `scheduleCloudPush` tenta PUT → rede cai / JSONBin retorna erro → o erro é logado no console mas nada aparece no ecrã → utilizador fecha o browser convicto de que os dados foram guardados → dados perdidos.  
**Ficheiro:** `scheduleCloudPush()` — bloco `catch` não exibe nenhum aviso ao utilizador.

---

### QA-05 · `deleteSprint` ativa o sprint errado após apagar o sprint ativo
**Fluxo:** Sprints criados por ordem: Sprint 3, Sprint 1, Sprint 2 (array `[3,1,2]`) → Sprint 2 é o ativo → utilizador apaga Sprint 2 → fallback ativa `sprints[sprints.length - 1]` = Sprint 2 (já apagado)... wait, Sprint 2 já foi filtrado, então ativa o último da lista por inserção = Sprint 2... na prática ativa o que estava na última posição do array antes do filtro, que pode não ser o "Sprint mais recente" do ponto de vista do utilizador.  
**Ficheiro:** `deleteSprint()` linha 2445  
**Fix conhecido:** Ordenar os sprints restantes antes de escolher o fallback (já registado em BUGS.md #3)

---

## Bugs de Média Prioridade (comportamento inesperado)

### QA-06 · Tecla Enter no campo SP (Story Points) não submete o formulário
**Fluxo:** Utilizador preenche US ID → US Name → Dev → SP → prime Enter → nada acontece. Todos os outros campos (US ID, US Name, Dev) ativam `addItem()` no Enter, mas o campo SP não.  
**Ficheiro:** `bindKeys()` linha 1482 — `itemPts` não tem listener de `keydown`.  
**Fix:** Adicionar `document.getElementById('itemPts').addEventListener('keydown', e => { if (e.key === 'Enter') addItem(); });`

---

### QA-07 · `max="100"` no input SP não é validado em JS — valores acima de 100 são aceites
**Fluxo:** O HTML tem `max="100"` no campo SP mas `parseInt(ptsVal) || 0` em `addItem()` aceita qualquer número positivo. Utilizador pode escrever 999 via teclado (browsers não bloqueiam a escrita, só o spinner HTML).  
**Ficheiro:** `addItem()` linha 1848; HTML linha 1033

---

### QA-08 · Nomes de sprint duplicados permitidos em `createSprint`
**Fluxo:** Utilizador cria "Sprint 3" → apaga "Sprint 2" → abre modal "Novo Sprint" → a sugestão é "Sprint 3" (já existe) → utilizador confirma → existem dois "Sprint 3" no dropdown sem forma de os distinguir.  
**Ficheiro:** `createSprint()` linha 2411 — sem verificação de nome duplicado.  
**Fix:** Verificar `db.sprints.some(s => s.name === name)` antes de criar.

---

### QA-09 · Sugestão de nome do modal de sprint pode colidir com nome existente
**Fluxo:** Sprints 1, 2, 3 existem → apagar Sprint 2 → modal sugere "Sprint 3" (2 sprints restantes + 1 = 3, que já existe).  
**Ficheiro:** `openNewSprintModal()` linha 2400  
**Fix conhecido:** Iterar nomes existentes para encontrar o próximo número livre (já registado em BUGS.md #4)

---

### QA-10 · `addItem` usa `Date.now().toString()` para IDs (inconsistente com importação Excel)
**Fluxo:** Em múltiplos cliques rápidos ou tabs paralelos, dois itens podem receber o mesmo timestamp como ID → `mergeFromCloud` trata-os como o mesmo item → um dos itens é silenciosamente sobrescrito.  
**Ficheiro:** `addItem()` linha 1849  
**Fix conhecido:** Substituir por `crypto.randomUUID()` (já registado em BUGS.md #5)

---

### QA-11 · Filtro por Dev persiste ao mudar de sprint (quando o dev existe em ambos)
**Fluxo:** Sprint A tem "Alice" → utilizador filtra por "Alice" → muda para Sprint B que também tem "Alice" → o filtro "Alice" fica ativo no Sprint B sem que o utilizador o tenha pedido. Apenas é resetado se "Alice" não existir no novo sprint.  
**Ficheiro:** `switchSprint()` não faz reset de `selectedDevFilter`.  
**Fix:** Adicionar `selectedDevFilter = 'all';` em `switchSprint`.

---

### ~~QA-12 · `applyConfig` não permite remover datas de um sprint~~ — ✅ Won't Fix (by design)
> Um sprint deve ter sempre datas definidas. Este comportamento é intencional.

---

### ~~QA-13 · Excel import: SP importado como `float`, UI usa `parseInt`~~ — ✅ Corrigido
> `importDataExcel` alterado para `parseInt` com clamp `[0, 21]`, consistente com `addItem` e `saveInlineEdit`.

---

### QA-14 · Filename do export Excel usa ID do sprint (timestamp) em vez do nome
**Comportamento:** Ficheiro exportado chama-se `sprint_1716123456789_export.xlsx` em vez de `sprint_Sprint 3_export.xlsx`.  
**Ficheiro:** `exportDataExcel()` linha 2510  
**Fix:** `XLSX.writeFile(workbook, \`sprint_${sprint.name}_export.xlsx\`)`

---

## Bugs de Baixa Prioridade (qualidade / UX menor)

### QA-15 · `deletedNames` e `deletedIds` crescem indefinidamente
**Impacto:** Em sprints com muitos adds/deletes, estes arrays nunca são limpos → payload JSON cresce → pode eventualmente exceder o limite de 100 KB do JSONBin Free Tier (mesmo com compressão LZ).  
**Ficheiro:** `deleteItem()` — sem poda dos arrays.

---

### QA-16 · Sem indicador de carregamento durante importação de Excel grande
**Fluxo:** Utilizador importa ficheiro com 500+ linhas → FileReader + SheetJS processam em background → UI parece congelada durante vários segundos sem nenhum spinner ou mensagem de "a processar".  
**Ficheiro:** `importDataExcel()` — `showSpinner()` não é chamado.

---

### QA-17 · `isSpillover` tem complexidade O(n × m) por item renderizado
**Impacto:** Para cada item do sprint atual, itera todos os sprints e todos os seus itens. Com 10 sprints de 30 itens, cada `renderItems()` faz 300 iterações por item visível → lag perceptível em dados volumosos.  
**Ficheiro:** `isSpillover()` linha 1948

---

### QA-18 · Modal não prende foco do teclado (Tab escapa para o fundo)
**Fluxo:** Utilizador abre modal "Novo Sprint" → prime Tab → o foco vai para elementos por trás do overlay em vez de ciclar pelos campos do modal.  
**Ficheiro:** `index.html` — nenhum listener de `keydown` prende Tab dentro dos modais.

---

### QA-19 · `saveDB` → `refreshAll` destrói e recria os gráficos Chart.js em cada checkbox
**Impacto:** Cada toggle de item (`toggleItem`) chama `saveDB` → `refreshAll` → `renderChart` + `renderReviewChart` → `existing.destroy()` + `new Chart(...)`. Com muitos itens, isto causa flicker visual e uso desnecessário de CPU.  
**Ficheiro:** `toggleItem()` → `saveDB()` → `refreshAll()`

---

### QA-20 · `getSprintCurrentDay` retorna 1 para sprints legados sem datas
**Impacto:** Sprints antigos sem `startDate`/`endDate` usam `sprint.currentDay || 1`. O gráfico mostra sempre "Dia 1" como dia atual, tornando o burndown inútil para dados históricos antigos.  
**Ficheiro:** `getSprintCurrentDay()` linha 1457

---

## Resumo

| Prioridade | Total | IDs |
|------------|-------|-----|
| Crítico    | 2     | QA-01, QA-02 |
| Alta       | 3     | QA-03, QA-04, QA-05 |
| Média      | 8     | QA-06 a QA-14 |
| Baixa      | 6     | QA-15 a QA-20 |
| **Total**  | **19** | |

> Bugs QA-01, QA-02, QA-05, QA-09, QA-10 já estão registados em BUGS.md com fix proposto.  
> Bugs novos neste relatório: QA-03, QA-04, QA-06, QA-07, QA-08, QA-11 a QA-20.
