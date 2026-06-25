# Sprint 01 - Migration and Data Preparation Planning

| Field | Value |
|---|---|
| Sprint | 01 |
| Goal | Approve the new claim-prediction dataset, rewrite project documentation, define the feature schema, and lock the preprocessing and EDA plan before implementation begins. |
| Status | In Progress |
| Start | 2026-06-21 |
| End | TBD |

---

## Scope

1. dataset validation against the approved local CSV files
2. PRD v2 rewrite
3. architecture and decision-log rewrite
4. feature schema and preprocessing-plan definition
5. agent responsibility update
6. migration inventory and phase sequencing

No code implementation, model training, or backend/frontend migration occurs in
this sprint.

---

## Exit Criteria

- [ ] PRD v2 approved
- [ ] architecture doc approved
- [ ] dataset doc approved
- [ ] feature schema approved
- [ ] preprocessing and EDA plan approved
- [ ] agent responsibilities approved
- [ ] migration inventory approved

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Legacy docs continue to reference the old dataset | High | High | Rewrite the active planning docs and role guides in one pass. |
| Preprocessing contract is underspecified | Medium | High | Lock field groups, parsing rules, and split rules before implementation. |
| Severe class imbalance is ignored in later modeling | High | High | Record the metric strategy now in docs and agent audits. |
| The unlabeled official `test.csv` is misused for evaluation | Medium | High | State the split rule clearly in every active planning file. |

---

## Artifacts

- Tasks: `todo/dev_todo.md`, `todo/qa_todo.md`
- Planning docs: `docs/PRD.md`, `docs/ARCHITECTURE.md`,
  `docs/knowledge/feature_schema.md`,
  `docs/knowledge/data_preparation_plan.md`, `docs/MIGRATION_PLAN.md`
