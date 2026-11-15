# Graph Report - nasa  (2026-11-14)

## Corpus Check
- Corpus is ~27,399 words - fits in a single context window. You may not need a graph.

## Summary
- 127 nodes · 177 edges · 17 communities (15 shown, 2 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 5 edges (avg confidence: 0.79)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16

## God Nodes (most connected - your core abstractions)
1. `DOC-01 Mapa Maestro` - 49 edges
2. `DOC-02 Genesis` - 32 edges
3. `TASKS` - 31 edges
4. `LB-1 Libro GPV` - 9 edges
5. `MO-2 Residuo 2 sigma` - 6 edges
6. `MO-1 Modelo nulo personal` - 5 edges
7. `MO-3 CUSUM bilateral` - 5 edges
8. `MO-6 El Contrapeso` - 5 edges
9. `DC-04 Libro GPV 9 presupuestos` - 5 edges
10. `DC-05 Alarma con recibo` - 4 edges

## Surprising Connections (you probably didn't know these)
- `Mandamiento 1 Nada lee directo de sensores` --references--> `LB-1 Libro GPV`  [EXTRACTED]
  CLAUDE.md → DOC-01_MAP-S1-mapa-maestro-sistema-v0.2.md
- `Tarea M1.1` --implements--> `LB-1 Libro GPV`  [EXTRACTED]
  TASKS.md → DOC-01_MAP-S1-mapa-maestro-sistema-v0.2.md
- `FB-001` --references--> `MO-1 Modelo nulo personal`  [EXTRACTED]
  DOC-02_MAP-S2-genesis-nueva-generacion-v0.3.md → DOC-01_MAP-S1-mapa-maestro-sistema-v0.2.md
- `Tarea M2.1` --implements--> `MO-1 Modelo nulo personal`  [EXTRACTED]
  TASKS.md → DOC-01_MAP-S1-mapa-maestro-sistema-v0.2.md
- `Tarea M2.2` --implements--> `MO-2 Residuo 2 sigma`  [EXTRACTED]
  TASKS.md → DOC-01_MAP-S1-mapa-maestro-sistema-v0.2.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Falsaciones FB-001..FB-008** — doc_02_map_s2_genesis_nueva_generacion_v0_3_fb_001, doc_02_map_s2_genesis_nueva_generacion_v0_3_fb_002, doc_02_map_s2_genesis_nueva_generacion_v0_3_fb_003, doc_02_map_s2_genesis_nueva_generacion_v0_3_fb_004, doc_02_map_s2_genesis_nueva_generacion_v0_3_fb_005, doc_02_map_s2_genesis_nueva_generacion_v0_3_fb_006, doc_02_map_s2_genesis_nueva_generacion_v0_3_fb_007, doc_02_map_s2_genesis_nueva_generacion_v0_3_fb_008 [EXTRACTED 1.00]
- **Pipeline Ingesta-Libro-Motor-Fabrica-Superficies** — doc_01_map_s1_mapa_maestro_sistema_v0_2_in_3, doc_01_map_s1_mapa_maestro_sistema_v0_2_lb_1, doc_01_map_s1_mapa_maestro_sistema_v0_2_mo_2, doc_01_map_s1_mapa_maestro_sistema_v0_2_fa_1, doc_01_map_s1_mapa_maestro_sistema_v0_2_su_5 [EXTRACTED 1.00]
- **Los 3 mandamientos** — claude_mandamiento_1, claude_mandamiento_2, claude_mandamiento_3 [EXTRACTED 1.00]

## Communities (17 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (24): DOC-02 Genesis, Ancla C-1, Ancla C-10, Ancla C-11, Ancla C-12, Ancla C-13, Ancla C-14, Ancla C-15 (+16 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (20): El Adversario, LA TORMENTA, FA-4 El Faro, IN-4 Banco de Falsaciones, TASKS, Tarea M0.1, Tarea M0.2, Tarea M0.4 (+12 more)

### Community 2 - "Community 2"
Cohesion: 0.10
Nodes (20): DOC-01 Mapa Maestro, DC-02 Canal B autorreporte, FA-2 N-of-1 ABAB, FM-1 familia de hipotesis, FM-10 familia de hipotesis, FM-2 familia de hipotesis, FM-3 familia de hipotesis, FM-4 familia de hipotesis (+12 more)

### Community 3 - "Community 3"
Cohesion: 0.14
Nodes (15): Mandamiento 1 Nada lee directo de sensores, Mandamiento 2 Preregistro hasheado antes de correr, LA SALA, DC-03 Canal C eventos fisicos, DC-04 Libro GPV 9 presupuestos, GO-2 Preregistro SHA-256, IN-3 SWPC/DONKI/OSDR, LB-1 Libro GPV (+7 more)

### Community 4 - "Community 4"
Cohesion: 0.29
Nodes (7): EL RESIDUO, DC-06 Stream de residuo, MO-2 Residuo 2 sigma, FB-001, Tarea M0.5, Tarea M2.2, Tarea M3.2

### Community 5 - "Community 5"
Cohesion: 0.40
Nodes (6): LA FUNDICION, El Guardian, DC-12 Contrato de Fundicion, FA-1 Kanban H-cards, DOC-04 La Fundicion, Tarea M4.2

### Community 6 - "Community 6"
Cohesion: 0.33
Nodes (6): Mandamiento 3 Colores solo con regla contestable, DC-05 Alarma con recibo, MO-3 CUSUM bilateral, SU-1 Alertas con recibo, FB-002, Tarea M2.3

### Community 7 - "Community 7"
Cohesion: 0.40
Nodes (5): DC-08 Cierre de conservacion, MO-6 El Contrapeso, FB-005, Tarea M1.2, Tarea M1.4

### Community 8 - "Community 8"
Cohesion: 0.67
Nodes (3): DC-01 Canal A sensores, IN-1, Tarea M0.3

### Community 9 - "Community 9"
Cohesion: 0.67
Nodes (3): DC-07 Capsula exportable, FA-3 Capsula, Tarea M3.6

### Community 10 - "Community 10"
Cohesion: 0.67
Nodes (3): DC-09 Forma diaria del habitat, MO-7 Forma diaria del habitat, FB-006

### Community 11 - "Community 11"
Cohesion: 0.67
Nodes (3): DC-10 Casos de error y contagio, GO-6 Epidemiologia del error, FB-007

### Community 12 - "Community 12"
Cohesion: 0.67
Nodes (3): DC-11 Ficha de vida de sensor, MO-8 Demografia de testigos, FB-008

### Community 13 - "Community 13"
Cohesion: 1.00
Nodes (3): MO-4 Triangulacion 3 testigos, FB-003, Tarea M2.4

### Community 14 - "Community 14"
Cohesion: 1.00
Nodes (3): MO-5 Integrador lento del agua, FB-004, Tarea M2.5

## Knowledge Gaps
- **59 isolated node(s):** `LEEME`, `auditoria`, `implementar`, `IN-2`, `FA-2 N-of-1 ABAB` (+54 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DOC-01 Mapa Maestro` connect `Community 2` to `Community 1`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 14`?**
  _High betweenness centrality (0.496) - this node is a cross-community bridge._
- **Why does `DOC-02 Genesis` connect `Community 0` to `Community 3`, `Community 4`, `Community 6`, `Community 7`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 14`?**
  _High betweenness centrality (0.355) - this node is a cross-community bridge._
- **Why does `TASKS` connect `Community 1` to `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 9`, `Community 13`, `Community 14`?**
  _High betweenness centrality (0.330) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `LB-1 Libro GPV` (e.g. with `IN-3 SWPC/DONKI/OSDR` and `MO-1 Modelo nulo personal`) actually correct?**
  _`LB-1 Libro GPV` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `LEEME`, `auditoria`, `implementar` to the rest of the system?**
  _59 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.08333333333333333 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._