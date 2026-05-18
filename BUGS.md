# Code Review — Lista de Bugs

## Já corrigidos ✅

| # | Descrição |
|---|-----------|
| ✅ | Boot race condition — cloud sobrescrevia alterações locais feitas durante o fetch |
| ✅ | Item ressurreição após rename — `deletedIds` adicionado ao lado de `deletedNames` |
| ✅ | Null guards em falta — `toggleItem`, `toggleInReview`, `openCommentModal`, `saveInlineEdit` |
| ✅ | IDs duplicados na importação Excel — substituído por `crypto.randomUUID()` |
| ✅ | Configuração do sprint não propagava entre utilizadores — `configUpdatedAt` por sprint |
| ✅ | Polling sobrescrevia dados locais — `mergeFromCloud` em vez de `db = cloudDB` |
| ✅ | `switchSprint` não fazia reset ao `currentPage` |
| ✅ | `saveInlineEdit` não verificava US IDs duplicados |
| ✅ | `populateSprintList` — `new Date(null)` quando só existia `startDate` |
| ✅ | `isSpillover` comparava por nome em vez de ID |
| ✅ | Sem `reader.onerror` no FileReader |
| ✅ | `backupDB` não chamava `URL.revokeObjectURL` |
| ✅ | CSS morto — `.tabs`, `.tab`, `.subnav`, `.subnav-tab` (~60 linhas) |
| ✅ | Função `isCurrentSprint` nunca chamada — dead code removido |

---

## Bugs pendentes

### Médios

**1. `renderChart` e `renderReviewChart` — divisão por zero quando `days = 0`**
- **Problema:** Se o sprint tiver datas cujos dias úteis são 0 (ex: início e fim no mesmo fim de semana), `getSprintDays` retorna 0. A linha `total / days` produz `Infinity`, corrompendo todos os dados do gráfico.
- **Fix:** Guardar `const safeDays = Math.max(days, 1)` e usar `safeDays` nos cálculos de ideal.

**2. `mergeFromCloud` — crash se `cloudSprint.items` for `undefined`**
- **Problema:** `cloudSprint.items.forEach(...)` crasha com `TypeError` se um sprint da cloud tiver o campo `items` ausente (dados corrompidos, backup antigo, ou sprint criado manualmente via API).
- **Fix:** Substituir por `(cloudSprint.items || []).forEach(...)`.

**3. `deleteSprint` — fallback activa o sprint errado**
- **Problema:** Ao apagar o sprint ativo, `latestDB.sprints[latestDB.sprints.length - 1]` activa o último por ordem de inserção no array, que pode não ser o último da ordem de apresentação (alfabética/numérica).
- **Fix:** Ordenar os sprints restantes antes de escolher o fallback.

**4. `openNewSprintModal` — sugestão de nome pode colidir**
- **Problema:** `db.sprints.length + 1` não considera sprints apagados. Exemplo: existem Sprints 1, 2, 3 → apagar Sprint 2 → modal sugere "Sprint 3" que já existe.
- **Fix:** Encontrar o próximo número disponível iterando os nomes existentes.

---

### Baixo / Qualidade

**5. `addItem` ainda usa `Date.now().toString()` para IDs**
- **Problema:** Inconsistente com a importação Excel que já usa `crypto.randomUUID()`. Com cliques rápidos em sequência, colisão de timestamp é improvável mas possível.
- **Fix:** Substituir `Date.now().toString()` por `crypto.randomUUID()`.

**~~6. Boot merge não actualiza `db.lastUpdated`~~ ✅**
- **Problema:** Quando o boot usa `mergeFromCloud` (local tinha dados), `db.lastUpdated` não é actualizado para o valor da cloud. O polling vai continuar a ver `cloudDB.lastUpdated > db.lastUpdated` como `true` e a fazer merges redundantes até que uma acção local actualize o timestamp.
- **Fix:** Após `mergeFromCloud` no boot, actualizar `db.lastUpdated = Math.max(db.lastUpdated || 0, cloudDB.lastUpdated || 0)`.

---

### Código morto

**~~7. CSS nunca usado — 5 definições~~ ✅**
- `.item-day-tag` — classe definida mas sem uso no HTML ou JS
- `--warn: #f5a623` — variável CSS definida mas sem referências
- `.sep` — classe definida mas sem uso
- `.topbar-sub` — classe definida mas sem uso
- `.btn-full` — classe definida mas sem uso
