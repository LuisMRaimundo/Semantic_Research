#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Single-screen Fase 0 workbench: search → decide → run → concordance."""

from __future__ import annotations

import json
import sys
import threading
import webbrowser
from pathlib import Path
from typing import Optional
from tkinter import filedialog, messagebox, scrolledtext, ttk
import tkinter as tk

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from semantic import decisions as decmod
from semantic.pipeline import run_class, search_and_seed
from semantic.settings import CLASSES_DIR, load_config
from semantic.workspace import ClassWorkspace

APP = "Semantic Research — Fase 0"
# Shared labels; atributo is PULO-only (Onto has no attribute bucket).
DECISION_CHOICES_PULO = ("", "UF", "RT", "exclude", "atributo")
DECISION_CHOICES_ONTO = ("", "UF", "RT", "exclude")
DECISION_LABELS = {
    "": "—",
    "UF": "UF",
    "RT": "RT",
    "exclude": "exclude",
    "atributo": "atributo",
}
# File-only / migrated evidence statuses (no PASSO 3 radio).
DECISIONS_FILE_ONLY = frozenset({"oposicao", "vizinha"})

GUIDE_TEXT = """\
SEMANTIC RESEARCH — QUICK GUIDE
════════════════════════════════

ORDEM DE TRABALHO (numerada — igual ao checklist do painel direito)
───────────────────────────────────────────────────────────────────
1 · CLASSE
   Criar/abrir a classe e preencher pref_label (lema preferido) e
   axis (a propriedade que define a classe).

2 · PESQUISAR   (2a antes de 2b)
   2a  PULO — âncora ILI, desambiguado por sentido. SEMPRE primeiro.
   2b  Onto.PT — cobertura difusa. Depois do PULO.
   Cada synset vira um cartão de sentido à esquerda.

3 · DECIDIR
   Para cada cartão, escolher um rótulo (ver Glossário).
   Opções por fonte:
     PULO  → — UF RT exclude atributo
     Onto  → — UF RT exclude   (sem atributo)
   (oposicao / vizinha: só por migração ou edição do ficheiro)

4 · GUARDAR DECISÕES
   Botão «4 · Guardar decisões». Escreve decisions.json.

5 · JUNÇÃO ILI  (automática — CILI)
   Sem ecrã de decisão. No Run, OEWN↔PULO resolve-se só pela tabela
   CILI (ili-map). Pares sem CILI ficam sem âncora partilhada.
   Mapeamentos humanos antigos: confirmados ∩ CILI; divergentes só
   no relatório ili_migration_report (não aplicados).

6 · RUN
   Botão «6 · ▶ Run»: compila decisões, corre PULO (+ Onto descoberta),
   WordNet/OWN-PT, junção CILI e LexWarrant (diagnóstico).

7 · TERMOS / FINAL_RESULTS
   Deliverable: TERMOS.html (consulta A–F) + TERMOS_PESQUISA.md/.csv.
   A concordância LexWarrant é diagnóstico interno.


What each source is for
───────────────────────
• PULO     — Portuguese WordNet; 1 synset = 1 sense; linked to ILI
             (Interlingual Index). Prefer this as the sense anchor.
• Onto.PT  — Discovery / triage only (PASSO 3). Does not admit vocabulary.
• WordNet  — OEWN (English), same folder WordNet\; search here in PASSO 2.
             Corroboration only (no UF/RT). Feeds WordNet/OWN-PT track + CILI join.
• LexWarrant — Relator only: joins results by ILI (or weakly by term).
             Reports agreement / divergence; does not decide.


Glossary — decision labels
──────────────────────────
UF          Used For / “é mesmo isto”
            The sense IS the class meaning (or a true synonym).
            Maps to SKOS altLabel (alternative lexical form of the
            preferred concept).

RT          Related Term / “parecido”
            Related but not identical — useful neighbour, not a
            synonym. Maps to skos:related.

exclude     “não interessa”
            Wrong sense / wrong domain. Dropped from the class
            (homograph / off-axis reading).

atributo    Quality noun — PULO only (evidence, not vocabulary)
            A noun naming the quality (not an adjective for the
            concept itself). Documented in Bloco B; never SKOS.
            Onto.PT has no atributo: use UF (or exclude) there.

oposicao    Declared opposition (evidence) — not a PASSO 3 button
            Legacy «contraste» migrates here automatically.
            Documented only; never a vocabulary relation.

vizinha     Remission to a neighbouring class’s organising principle
            File-only / manual reclassification from oposicao.
            Documented only; never a vocabulary relation.

—           (blank)
            Not decided yet. Pipeline will refuse incomplete senses
            when compiling a full run; mark every card before Run.


Glossary — other terms
──────────────────────
class / class_id
            One conceptual category you are grounding lexically
            (any research target — not tied to a fixed vocabulary).

pref_label  Preferred lemma for the class (display / SKOS prefLabel).

axis        Defining property used in adjudication tests
            (what must stay true for UF).

sense / synset
            One meaning: a set of synonyms + gloss. Decisions are
            per sense, not per spelling.

ILI         Interlingual Index (ili-30-… / CILI i…): shared concept
            id across wordnets. Primary join key in LexWarrant.

lemma       Dictionary citation form (not inflected).

concordance Matrix of terms × sources with verdicts:
            convergência plena · divergência de relação ·
            fonte única · sinalização.

proposta_final
            LexWarrant suggestion only — human must still adjudicate.

convergência
            ≥2 sources agree on the same status for a term.

divergência
            Sources disagree (e.g. ONTO=UF vs PULO=atributo).
            Kept visible on the worklist — never collapsed by vote.

weak(term)  Join by normalised spelling when no shared ILI
            (typical for Onto.PT). Lower confidence than ILI join.


Files you care about
────────────────────
classes/<Class>/FINAL_RESULTS__Onto_plus_PULO/
    OPEN_ME__FINAL_RESULTS.html     ← green splash (open this)
    FINAL__Onto_plus_PULO__….md     ← concordance (human)
    FINAL__Onto_plus_PULO__….json   ← concordance (machine)
classes/<Class>/decisions.json      ← curated choices
classes/<Class>/out/                ← scratch + PULO signals


Tip
───
Mark PULO senses first (ILI anchor), then Onto.PT for coverage.
When concordance shows divergência, that is a finding, not a bug.

PULO “sinalização” (#NN / similar-to)
─────────────────────────────────────
The PULO engine auto-harvests many related lemmas into sinalização.
Those are NOT your decisions. By default the workbench parks them in
out/<Class>.PULO.signals.md and keeps the main concordance short.
Set "hide_pulo_signals": false in config.json to include them again.
"""



class Workbench(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP)
        self.geometry("1180x780")
        self.minsize(960, 640)
        self.class_var = tk.StringVar()
        self.source_var = tk.StringVar(value="pulo")
        self.filter_var = tk.StringVar(value="pulo")  # which sense cards to show
        self.query_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="Starts with")
        self.status_var = tk.StringVar(value="Ready")
        self._sense_vars: dict[str, tk.StringVar] = {}
        self._guide_win: tk.Toplevel | None = None
        self._build()
        self.bind("<F1>", lambda e: self._open_guide())
        self._refresh_classes()

    def _build(self):
        top = ttk.LabelFrame(self, text="PASSO 1 · Classe  (criar/abrir; preencher pref_label e axis)",
                             padding=8)
        top.pack(fill="x", padx=10, pady=(8, 0))
        ttk.Label(top, text="Class").pack(side="left")
        self.class_combo = ttk.Combobox(top, textvariable=self.class_var, width=28)
        self.class_combo.pack(side="left", padx=6)
        self.class_combo.bind("<<ComboboxSelected>>", lambda e: self._load_class())
        ttk.Button(top, text="New…", command=self._new_class).pack(side="left")
        ttk.Button(top, text="Rename…", command=self._rename_class).pack(
            side="left", padx=(4, 0)
        )
        ttk.Button(top, text="Open folder", command=self._open_folder).pack(
            side="left", padx=4
        )
        ttk.Button(top, text="↻", width=3, command=self._load_class).pack(side="left")
        ttk.Button(top, text="? Guide", command=self._open_guide).pack(
            side="right"
        )

        search = ttk.LabelFrame(
            self,
            text="PASSO 2 · Pesquisar  (PULO → Onto.PT → WordNet/OEWN — tudo nesta janela)",
            padding=8)
        search.pack(fill="x", padx=10, pady=(0, 6))
        ttk.Radiobutton(
            search, text="PULO  — ILI / WordNet.PT",
            variable=self.source_var, value="pulo",
            command=self._sync_filter_to_search,
        ).pack(side="left")
        ttk.Radiobutton(
            search, text="Onto.PT  — fuzzy / coverage",
            variable=self.source_var, value="onto",
            command=self._sync_filter_to_search,
        ).pack(side="left", padx=(8, 0))
        ttk.Radiobutton(
            search, text="WordNet  — OEWN (EN)",
            variable=self.source_var, value="wordnet",
            command=self._sync_filter_to_search,
        ).pack(side="left", padx=(8, 12))
        ttk.Entry(search, textvariable=self.query_var, width=28).pack(side="left")
        ttk.Combobox(search, textvariable=self.mode_var, width=12,
                     values=("Starts with", "Contains", "Exact"),
                     state="readonly").pack(side="left", padx=6)
        ttk.Button(search, text="Search", command=self._search).pack(side="left")

        mid = ttk.Panedwindow(self, orient="horizontal")
        mid.pack(fill="both", expand=True, padx=10, pady=4)

        left = ttk.Frame(mid)
        right = ttk.LabelFrame(
            mid,
            text="PASSOS 4–7 · Guardar → Run (CILI auto) → TERMOS",
            padding=6,
        )
        mid.add(left, weight=3)
        mid.add(right, weight=2)

        filt = ttk.LabelFrame(
            left, text="PASSO 3 · Decidir sentidos — mostrar cartões de", padding=6)
        filt.pack(fill="x")
        ttk.Radiobutton(
            filt, text="PULO only", variable=self.filter_var, value="pulo",
            command=self._render_senses,
        ).pack(side="left")
        ttk.Radiobutton(
            filt, text="Onto.PT only", variable=self.filter_var, value="onto",
            command=self._render_senses,
        ).pack(side="left", padx=8)
        ttk.Radiobutton(
            filt, text="WordNet only", variable=self.filter_var, value="wordnet",
            command=self._render_senses,
        ).pack(side="left", padx=8)
        ttk.Radiobutton(
            filt, text="All", variable=self.filter_var, value="all",
            command=self._render_senses,
        ).pack(side="left")
        self.decide_hint = ttk.Label(filt, text="", foreground="#333")
        self.decide_hint.pack(side="left", padx=12)

        cards_box = ttk.Frame(left)
        cards_box.pack(fill="both", expand=True, pady=(4, 0))
        self.sense_canvas = tk.Canvas(cards_box, highlightthickness=0)
        self.sense_scroll = ttk.Scrollbar(
            cards_box, orient="vertical", command=self.sense_canvas.yview
        )
        self.sense_frame = tk.Frame(self.sense_canvas)  # tk.Frame → colored cards
        self.sense_frame.bind(
            "<Configure>",
            lambda e: self.sense_canvas.configure(
                scrollregion=self.sense_canvas.bbox("all")
            ),
        )
        self.sense_canvas.create_window((0, 0), window=self.sense_frame, anchor="nw")
        self.sense_canvas.configure(yscrollcommand=self.sense_scroll.set)
        self.sense_canvas.pack(side="left", fill="both", expand=True)
        self.sense_scroll.pack(side="right", fill="y")

        btnrow = ttk.Frame(left)
        btnrow.pack(fill="x", pady=(6, 0))
        ttk.Button(btnrow, text="4 · Guardar decisões",
                   command=self._save_decisions).pack(side="left")
        ttk.Button(btnrow, text="? Guide", command=self._open_guide).pack(
            side="left", padx=8
        )

        self.steps_box = tk.Label(
            right, text="", justify="left", anchor="w",
            font=("Consolas", 9), bg="#F4F6F8", padx=8, pady=6,
        )
        self.steps_box.pack(fill="x", pady=(0, 6))

        ttk.Label(right, text="Meta (axis / pref label)", font=("", 9, "bold")).pack(
            anchor="w"
        )
        self.meta_box = scrolledtext.ScrolledText(right, height=5, wrap="word")
        self.meta_box.pack(fill="x", pady=(0, 6))

        runrow = ttk.Frame(right)
        runrow.pack(fill="x")
        ttk.Label(
            runrow, text="5 · ILI=CILI (auto)", foreground="#555",
        ).pack(side="left")
        ttk.Button(runrow, text="6 · ▶ Run", command=self._run).pack(
            side="left", padx=6)
        ttk.Button(
            runrow, text="7 · TERMOS / FINAL",
            command=self._open_final_results,
        ).pack(side="left", padx=(0, 6))
        ttk.Button(
            runrow, text="concordância",
            command=self._open_concordance,
        ).pack(side="left")

        self.final_banner = tk.Label(
            right,
            text="Deliverable: TERMOS.html + TERMOS_PESQUISA.md/.csv  (+ CONCEPT.ttl)",
            bg="#1B5E20", fg="white", font=("", 9, "bold"),
            anchor="w", padx=8, pady=4,
        )
        self.final_banner.pack(fill="x", pady=(8, 0))

        # Onto→ILI review (GUI — not CLI-only)
        ili_box = ttk.LabelFrame(
            right,
            text="Onto→ILI · propor / aceitar / rejeitar (inventário)",
            padding=4,
        )
        ili_box.pack(fill="both", expand=False, pady=(8, 0))
        ili_btns = ttk.Frame(ili_box)
        ili_btns.pack(fill="x")
        ttk.Button(ili_btns, text="Propor", command=self._onto_ili_propose).pack(
            side="left"
        )
        ttk.Button(ili_btns, text="↻", width=3, command=self._onto_ili_refresh).pack(
            side="left", padx=4
        )
        ttk.Button(ili_btns, text="Aceitar", command=self._onto_ili_accept).pack(
            side="left", padx=4
        )
        ttk.Button(ili_btns, text="Rejeitar", command=self._onto_ili_reject).pack(
            side="left"
        )
        ttk.Button(
            ili_btns, text="Aceitar top-5", command=self._onto_ili_accept_top
        ).pack(side="left", padx=4)
        self.onto_ili_status = ttk.Label(ili_box, text="—", foreground="#444")
        self.onto_ili_status.pack(anchor="w", pady=(2, 2))
        self.onto_ili_list = tk.Listbox(ili_box, height=6, font=("Consolas", 8))
        self.onto_ili_list.pack(fill="both", expand=True)
        self._onto_ili_rows: list[dict] = []

        self.log = scrolledtext.ScrolledText(right, height=12, wrap="word")
        self.log.pack(fill="both", expand=True, pady=(8, 0))

        ttk.Label(self, textvariable=self.status_var, relief="sunken",
                  anchor="w", padding=(6, 2)).pack(fill="x", side="bottom")


    def _open_guide(self):
        """Show the quick-reference guide (steps + glossary)."""
        if self._guide_win is not None and self._guide_win.winfo_exists():
            self._guide_win.lift()
            self._guide_win.focus_force()
            return
        win = tk.Toplevel(self)
        self._guide_win = win
        win.title("Quick guide & glossary")
        win.geometry("640x720")
        win.minsize(480, 400)
        win.transient(self)

        bar = ttk.Frame(win, padding=(10, 8))
        bar.pack(fill="x")
        ttk.Label(bar, text="Quick guide & glossary",
                  font=("", 12, "bold")).pack(side="left")
        ttk.Button(bar, text="Close", command=win.destroy).pack(side="right")

        body = scrolledtext.ScrolledText(
            win, wrap="word", font=("Consolas", 10), padx=12, pady=10
        )
        body.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        body.insert("1.0", GUIDE_TEXT)

        body.tag_configure("header", font=("Consolas", 10, "bold"))
        body.tag_configure("term", font=("Consolas", 10, "bold"),
                           foreground="#1a4a7a")
        for header in (
            "SEMANTIC RESEARCH — QUICK GUIDE",
            "Daily path (3 steps)",
            "What each source is for",
            "Glossary — decision labels",
            "Glossary — other terms",
            "Files you care about",
            "Tip",
        ):
            start = "1.0"
            while True:
                idx = body.search(header, start, stopindex="end")
                if not idx:
                    break
                end = f"{idx}+{len(header)}c"
                body.tag_add("header", idx, end)
                start = end
        for term in (
            "UF", "RT", "exclude", "atributo", "oposicao", "vizinha",
            "ILI", "pref_label", "axis", "concordance",
            "proposta_final", "convergência", "divergência", "weak(term)",
        ):
            start = "1.0"
            while True:
                idx = body.search(term, start, stopindex="end")
                if not idx:
                    break
                line, col = body.index(idx).split(".")
                end = f"{idx}+{len(term)}c"
                if int(col) <= 2:
                    body.tag_add("term", idx, end)
                start = end
        body.configure(state="disabled")

        def _on_close():
            self._guide_win = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", _on_close)
        win.bind("<Escape>", lambda e: _on_close())

    # -- class mgmt ------------------------------------------------------
    def _refresh_classes(self, select: str | None = None):
        names = ClassWorkspace.list_classes()
        self.class_combo["values"] = names
        if select and select in names:
            self.class_var.set(select)
        elif names and not self.class_var.get():
            self.class_var.set(names[0])
        if self.class_var.get():
            self._load_class()

    def _new_class(self):
        win = tk.Toplevel(self)
        win.title("New class")
        win.transient(self)
        cid = tk.StringVar()
        pref = tk.StringVar()
        axis = tk.StringVar()
        for i, (lab, var) in enumerate((
            ("class_id", cid), ("pref_label", pref), ("axis", axis)
        )):
            ttk.Label(win, text=lab).grid(row=i, column=0, sticky="w", padx=8, pady=4)
            ttk.Entry(win, textvariable=var, width=40).grid(
                row=i, column=1, padx=8, pady=4
            )
        slug_preview = ttk.Label(win, text="", foreground="#555")
        slug_preview.grid(row=3, column=0, columnspan=2, sticky="w", padx=8)

        def _preview(*_a):
            raw = cid.get().strip()
            if not raw:
                slug_preview.configure(text="")
                return
            try:
                from semantic.workspace import slug_class
                slug_preview.configure(
                    text=f"Folder id: {slug_class(raw)}  (accents → ASCII)"
                )
            except ValueError:
                slug_preview.configure(text="")

        cid.trace_add("write", _preview)

        def ok():
            if not cid.get().strip():
                messagebox.showerror(APP, "class_id required")
                return
            from semantic.workspace import slug_class
            new_id = slug_class(cid.get().strip())
            ClassWorkspace.create(
                cid.get().strip(),
                pref_label=pref.get().strip(),
                axis=axis.get().strip(),
            )
            win.destroy()
            self._refresh_classes(select=new_id)

        ttk.Button(win, text="Create", command=ok).grid(
            row=4, column=1, sticky="e", padx=8, pady=10
        )

    def _rename_class(self):
        ws = self._ws()
        if not ws:
            messagebox.showinfo(APP, "Open a class first.")
            return
        win = tk.Toplevel(self)
        win.title(f"Rename class — {ws.class_id}")
        win.transient(self)
        ttk.Label(win, text="Current").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        ttk.Label(win, text=ws.class_id).grid(row=0, column=1, sticky="w", padx=8, pady=4)
        new_var = tk.StringVar(value=ws.class_id)
        ttk.Label(win, text="New class_id").grid(
            row=1, column=0, sticky="w", padx=8, pady=4
        )
        ttk.Entry(win, textvariable=new_var, width=40).grid(
            row=1, column=1, padx=8, pady=4
        )
        slug_preview = ttk.Label(win, text="", foreground="#555")
        slug_preview.grid(row=2, column=0, columnspan=2, sticky="w", padx=8)
        ttk.Label(
            win,
            text="Renames the folder and id only — decisions, senses, "
                 "pref_label and results stay the same. "
                 "Accents fold to ASCII (Compósita → Composita).",
            wraplength=360,
            foreground="#333",
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=8, pady=(0, 4))

        def _preview(*_a):
            raw = new_var.get().strip()
            if not raw:
                slug_preview.configure(text="")
                return
            try:
                from semantic.workspace import slug_class
                slug_preview.configure(text=f"Folder id: {slug_class(raw)}")
            except ValueError:
                slug_preview.configure(text="")

        new_var.trace_add("write", _preview)
        _preview()

        def ok():
            raw = new_var.get().strip()
            if not raw:
                messagebox.showerror(APP, "New class_id required")
                return
            try:
                from semantic.workspace import slug_class
                new_id = slug_class(raw)
            except ValueError as exc:
                messagebox.showerror(APP, str(exc))
                return
            if new_id == ws.class_id:
                win.destroy()
                return
            if not messagebox.askyesno(
                APP,
                f"Rename «{ws.class_id}» → «{new_id}»?\n\n"
                "Only the class name/folder changes.",
            ):
                return
            try:
                renamed = ws.rename(raw)
            except (FileExistsError, FileNotFoundError, ValueError) as exc:
                messagebox.showerror(APP, str(exc))
                return
            win.destroy()
            self._refresh_classes(select=renamed.class_id)
            self._log(f"Renamed {ws.class_id} → {renamed.class_id}\n")

        ttk.Button(win, text="Rename", command=ok).grid(
            row=4, column=1, sticky="e", padx=8, pady=10
        )

    def _ws(self) -> ClassWorkspace | None:
        name = self.class_var.get().strip()
        if not name:
            return None
        try:
            return ClassWorkspace.open(name)
        except FileNotFoundError:
            return None

    def _render_steps(self, ws):
        """Checklist numerado e vivo: ✓ feito · ▶ próximo · ○ pendente."""
        from semantic import decisions as _dec

        meta = ws.load_meta()
        dec = _dec.load_decisions(ws.decisions_json)
        senses = dec.get("senses") or []
        n_pulo = sum(1 for s in senses if (s.get("source") or "") == "pulo")
        n_onto = sum(1 for s in senses if (s.get("source") or "") == "onto")
        decided = sum(1 for s in senses if (s.get("decision") or "").strip())
        has_run = (ws.results / f"{ws.class_id}.PULO.result.json").exists()
        has_termos = (
            (ws.final_results / "TERMOS.html").exists()
            or (ws.final_results / "TERMOS_PESQUISA.md").exists()
        )
        has_final = ws.concordance_md().exists() or has_termos

        steps = [
            ("1", "Classe criada + meta (pref_label, axis)",
             bool(meta.get("pref_label")) and bool(meta.get("axis")), False),
            ("2a", f"Pesquisar PULO  ({n_pulo} cartões)", n_pulo > 0, False),
            ("2b", f"Onto.PT descoberta  ({n_onto} cartões)", n_onto > 0, True),
            ("3", f"Decidir sentidos  ({decided}/{len(senses)})",
             len(senses) > 0 and decided == len(senses), False),
            ("4", "Guardar decisões", len(senses) > 0 and decided == len(senses),
             False),
            ("5", "Junção ILI = CILI (automático no Run)", True, True),
            ("6", "▶ Run (PULO + fusão CILI)", has_run and has_final, False),
            ("7", "TERMOS / FINAL_RESULTS", has_final, False),
        ]
        lines = ["ORDEM DE TRABALHO"]
        next_marked = False
        for num, txt, done, optional in steps:
            if done:
                mark = "✓"
            elif not next_marked and not optional:
                mark = "▶"
                next_marked = True
            else:
                mark = "○"
            suffix = "   (opcional)" if optional and not done else ""
            lines.append(f" {mark} {num:>2} · {txt}{suffix}")
        self.steps_box.configure(text="\n".join(lines))

    def _load_class(self):
        ws = self._ws()
        if not ws:
            return
        self._render_steps(ws)
        meta = ws.load_meta()
        self.meta_box.delete("1.0", "end")
        self.meta_box.insert(
            "1.0",
            f"pref_label: {meta.get('pref_label', '')}\n"
            f"axis: {meta.get('axis', '')}\n"
            f"focus_stems: {', '.join(meta.get('focus_stems') or [])}\n",
        )
        self._render_senses()
        st = ws.status()
        self.status_var.set(
            f"{st['class_id']} · {st['senses_decided']}/{st['senses_total']} decided · "
            f"{st['next_step']}"
        )
        self._log_clear()
        self._log(f"Loaded {ws.class_id}\nNext: {st['next_step']}\n")
        conc = ws.concordance_md()
        if conc.exists():
            self._log("\n--- FINAL RESULTS (Onto + PULO) ---\n")
            self._log(f"{conc}\n\n")
            self._log(conc.read_text(encoding="utf-8")[:8000])
            self.final_banner.configure(
                text=f"FINAL RESULTS ready → {ws.final_results}",
                bg="#1B5E20",
            )
        else:
            self.final_banner.configure(
                text="Deliverable folder:  FINAL_RESULTS/  (empty until you Run)",
                bg="#555555",
            )
        self._onto_ili_refresh()

    def _open_folder(self):
        ws = self._ws()
        path = ws.root if ws else CLASSES_DIR
        path.mkdir(parents=True, exist_ok=True)
        try:
            import os
            os.startfile(path)  # type: ignore[attr-defined]
        except Exception:
            webbrowser.open(path.as_uri())

    # -- senses ----------------------------------------------------------
    def _sync_filter_to_search(self):
        """When user switches search lexicon, show that source's cards."""
        self.filter_var.set(self.source_var.get())
        self._render_senses()

    def _choices_for(self, source: str) -> tuple[str, ...]:
        src = (source or "").lower()
        if src == "onto":
            return DECISION_CHOICES_ONTO
        return DECISION_CHOICES_PULO

    def _update_decide_hint(self):
        f = self.filter_var.get()
        if f == "onto":
            self.decide_hint.configure(
                text="Onto options:  —  UF  RT  exclude   (NO atributo)"
            )
        elif f == "pulo":
            self.decide_hint.configure(
                text="PULO options:  —  UF  RT  exclude  atributo"
            )
        elif f == "wordnet":
            self.decide_hint.configure(
                text="WordNet: corroboration only (no UF/RT) — CILI join no Run"
            )
        else:
            self.decide_hint.configure(
                text="All · blue=PULO · amber=Onto · green=WordNet (info only)"
            )

    def _render_senses(self):
        for child in self.sense_frame.winfo_children():
            child.destroy()
        self._sense_vars.clear()
        self._update_decide_hint()
        ws = self._ws()
        if not ws:
            return
        dec = decmod.load_decisions(ws.decisions_json)
        senses = dec.get("senses") or []
        filt = self.filter_var.get()
        if filt in ("pulo", "onto", "wordnet"):
            senses = [s for s in senses if (s.get("source") or "").lower() == filt]

        if not senses:
            msg = "No senses yet. Search a lemma above (PULO / Onto / WordNet)."
            if filt == "pulo":
                msg = "No PULO cards. Search with «PULO — ILI» selected."
            elif filt == "onto":
                msg = "No Onto.PT cards. Search with «Onto.PT» selected."
            elif filt == "wordnet":
                msg = ("No WordNet cards. Search an English lemma with "
                       "«WordNet — OEWN» (e.g. composite, compound).")
            tk.Label(
                self.sense_frame, text=msg, fg="#555", anchor="w", justify="left"
            ).pack(anchor="w", padx=8, pady=12)
            return

        for s in senses:
            sk = decmod.sense_key(s["source"], s["key"])
            src = (s.get("source") or "").lower()
            if src == "onto":
                bg, accent, banner = "#FFF6E5", "#8A5A00", (
                    "Onto.PT  ·  fuzzy coverage  ·  options: UF · RT · exclude"
                )
                key_line = f"id: {s.get('key')}"
            elif src == "wordnet":
                bg, accent, banner = "#E8F5E9", "#1B5E20", (
                    "WordNet (OEWN)  ·  corroboration  ·  no UF/RT — junção CILI no Run"
                )
                key_line = (
                    f"OEWN ILI: {s.get('ili') or '—'}   ·   "
                    f"{s.get('local_id') or s.get('key')}"
                )
            else:
                bg, accent, banner = "#E8F1FB", "#0B3D6E", (
                    "PULO  ·  ILI anchor  ·  options: UF · RT · exclude · atributo"
                )
                key_line = f"ILI: {s.get('ili') or '—'}   ·   {s.get('key')}"

            card = tk.Frame(
                self.sense_frame, bg=bg, highlightbackground=accent,
                highlightthickness=2, padx=8, pady=6,
            )
            card.pack(fill="x", padx=4, pady=5)
            tk.Label(
                card, text=banner, bg=bg, fg=accent,
                font=("", 9, "bold"), anchor="w",
            ).pack(fill="x")
            tk.Label(
                card, text=key_line, bg=bg, fg="#444", anchor="w"
            ).pack(fill="x")
            members = ", ".join(s.get("members") or [])
            gloss = s.get("gloss") or "(no gloss)"
            tk.Label(
                card, text=members or "(no members)", bg=bg,
                font=("", 10, "bold"), wraplength=520, justify="left", anchor="w",
            ).pack(fill="x", pady=(4, 0))
            tk.Label(
                card, text=gloss, bg=bg, fg="#333",
                wraplength=520, justify="left", anchor="w",
            ).pack(fill="x", pady=(2, 4))

            if src == "wordnet":
                tk.Label(
                    card,
                    text="Info only — export saved under exports/*.facets.json "
                         "for WordNet track / Run.",
                    bg=bg, fg="#336633", anchor="w",
                ).pack(fill="x")
                continue
            choice_set = self._choices_for(src)
            raw = s.get("decision") or ""
            if src == "onto" and raw == "atributo":
                raw = "UF"
            # Preserve file-only evidence statuses (oposicao/vizinha); do not wipe.
            if raw in choice_set:
                initial = raw
            elif raw in DECISIONS_FILE_ONLY:
                initial = raw
            else:
                initial = ""
            var = tk.StringVar(value=initial)
            self._sense_vars[sk] = var
            row = tk.Frame(card, bg=bg)
            row.pack(anchor="w")
            tk.Label(row, text="Decide:", bg=bg, fg=accent,
                     font=("", 9, "bold")).pack(side="left", padx=(0, 6))
            for lab in choice_set:
                show = DECISION_LABELS.get(lab, lab or "—")
                tk.Radiobutton(
                    row, text=show, value=lab, variable=var,
                    bg=bg, activebackground=bg, selectcolor=bg,
                    highlightthickness=0,
                ).pack(side="left", padx=2)
            if raw in DECISIONS_FILE_ONLY:
                mig = " · migrado de contraste" if s.get("migrado_de") == "contraste" else ""
                rev = " · revisão pendente" if s.get("revisao_pendente") else ""
                tk.Label(
                    card,
                    text=f"Evidência (ficheiro): {raw}{mig}{rev}",
                    bg=bg, fg="#6B3A00", anchor="w",
                ).pack(fill="x", pady=(2, 0))

    def _save_decisions(self):
        ws = self._ws()
        if not ws:
            return
        # persist meta edits
        text = self.meta_box.get("1.0", "end")
        meta = ws.load_meta()
        for line in text.splitlines():
            if line.startswith("pref_label:"):
                meta["pref_label"] = line.split(":", 1)[1].strip()
            elif line.startswith("axis:"):
                meta["axis"] = line.split(":", 1)[1].strip()
            elif line.startswith("focus_stems:"):
                raw = line.split(":", 1)[1].strip()
                meta["focus_stems"] = [x.strip() for x in raw.split(",") if x.strip()]
        ws.save_meta(meta)

        dec = decmod.load_decisions(ws.decisions_json)
        migrated = bool(dec.get(decmod._MIGRATION_FLAG))
        for s in dec.get("senses", []):
            sk = decmod.sense_key(s["source"], s["key"])
            if sk in self._sense_vars:
                s["decision"] = self._sense_vars[sk].get()
        decmod.save_decisions(ws.decisions_json, dec)
        msg = "Decisions saved."
        if migrated:
            msg += " (migração contraste→oposicao gravada; .bak-AAAAMMDD criado)"
        self.status_var.set(msg)
        self._load_class()

    # -- search / run ----------------------------------------------------
    def _search(self):
        ws = self._ws()
        q = self.query_var.get().strip()
        if not ws or not q:
            messagebox.showinfo(APP, "Pick a class and type a query.")
            return
        source = (self.source_var.get() or "").strip().lower()
        self.status_var.set("Searching…")
        self.update_idletasks()

        # OEWN/`wn` uses SQLite with thread affinity (same constraint as
        # WordNet/wordnet_gui_v2.py). Must run on the Tk main thread.
        if source in ("wordnet", "oewn", "wn"):
            try:
                info = search_and_seed(
                    ws.class_id, q, source=source, mode=self.mode_var.get(),
                )
                self._search_done(info, None)
            except Exception as exc:  # noqa: BLE001
                self._search_done(None, exc)
            return

        def work():
            try:
                info = search_and_seed(
                    ws.class_id, q, source=source, mode=self.mode_var.get(),
                )
                # Bind defaults now — after() runs later; except-bound names are cleared.
                self.after(0, lambda i=info: self._search_done(i, None))
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda e=exc: self._search_done(None, e))

        threading.Thread(target=work, daemon=True).start()

    def _search_done(self, info, err):
        if err:
            messagebox.showerror(APP, str(err))
            self.status_var.set("Search failed.")
            return
        self._log(
            f"Search OK · {info['count']} synsets · "
            f"{info['senses_total']} sense cards "
            f"({info['undecided']} undecided)\n"
            f"export: {info['export']}\n"
        )
        if int(info.get("count") or 0) == 0:
            src = self.source_var.get()
            tip = (
                "WordNet expects an English citation form."
                if src == "wordnet"
                else "Try another spelling / citation form attested in the lexicon."
            )
            messagebox.showwarning(
                APP,
                "Search returned 0 synsets — the export is empty.\n\n"
                f"{tip}",
            )
            self.status_var.set("Search: 0 hits.")
        self._load_class()

    def _run(self):
        ws = self._ws()
        if not ws:
            return
        self._save_decisions()
        meta = ws.load_meta()
        if not (meta.get("axis") or "").strip():
            messagebox.showerror(
                APP,
                "axis is empty.\n\n"
                "In Meta (right panel) set the defining property, e.g.\n"
                "  axis: <what must hold for a UF decision>\n"
                "then «4 · Guardar decisões», then Run again.",
            )
            self.status_var.set("Run blocked — fill axis.")
            return
        self.status_var.set("Running pipeline…")
        self._log("\n▶ Running…\n")

        def work():
            try:
                summary = run_class(ws.class_id)
                self.after(0, lambda s=summary: self._run_done(s, None))
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda e=exc: self._run_done(None, e))

        threading.Thread(target=work, daemon=True).start()

    def _run_done(self, summary, err):
        if err:
            messagebox.showerror(APP, str(err))
            self.status_var.set("Run failed.")
            return
        # Refresh TERMOS on the Tk thread: OEWN/`wn` SQLite is thread-sticky,
        # so EN poles (A–D) written inside the worker can come out empty.
        ws = self._ws()
        if ws and summary.get("merge_ok"):
            try:
                from semantic.termos_pesquisa import write_termos_pesquisa
                paths = write_termos_pesquisa(ws, dest_dir=ws.final_results)
                summary["termos_pesquisa"] = paths
                self._log(
                    f"TERMOS refreshed (main thread) → {paths.get('html')}\n"
                )
            except Exception as exc:  # noqa: BLE001
                self._log(f"TERMOS refresh failed: {exc}\n")
                summary.setdefault("errors", []).append(f"TERMOS refresh: {exc}")
        self._log(json.dumps(
            {k: v for k, v in summary.items() if k != "status"},
            ensure_ascii=False, indent=2,
        ) + "\n")
        if summary.get("errors"):
            self._log("Errors:\n- " + "\n- ".join(summary["errors"]) + "\n")
        md = summary.get("concordance_md")
        if summary.get("final_results"):
            self._log(f"\nFINAL RESULTS (Onto + PULO) → {summary['final_results']}\n")
        if summary.get("note"):
            self._log(summary["note"] + "\n")
        if md and Path(md).exists():
            self._log("\n--- concordance ---\n")
            self._log(Path(md).read_text(encoding="utf-8")[:12000])
        self.status_var.set(
            "Done — see FINAL_RESULTS/"
            if summary.get("merge_ok")
            else "Finished with issues."
        )
        self._load_class()

    def _open_final_results(self):
        ws = self._ws()
        if not ws:
            return
        ws.ensure()
        # Prefer the bright HTML splash; else the folder
        html = ws.final_results / "OPEN_ME__FINAL_RESULTS.html"
        path = html if html.exists() else ws.final_results
        try:
            import os
            os.startfile(path)  # type: ignore[attr-defined]
        except Exception:
            webbrowser.open(path.as_uri())

    def _open_concordance(self):
        """Show concordance in-app (never os.startfile on .md — Cursor may own it)."""
        ws = self._ws()
        if not ws:
            return
        path = ws.concordance_md()
        if not path.exists():
            messagebox.showinfo(
                APP,
                "Ainda não há concordância em FINAL_RESULTS — "
                "execute «6 · ▶ Run» primeiro.",
            )
            return
        win = tk.Toplevel(self)
        win.title(f"Concordância — {ws.class_id}")
        win.geometry("900x700")
        win.minsize(640, 480)
        win.transient(self)
        bar = ttk.Frame(win, padding=(8, 6))
        bar.pack(fill="x")
        ttk.Label(bar, text=str(path), foreground="#555").pack(
            side="left", fill="x", expand=True
        )

        def open_folder():
            folder = path.parent
            try:
                import os
                os.startfile(folder)  # type: ignore[attr-defined]
            except Exception:
                webbrowser.open(folder.as_uri())

        def open_external():
            # Prefer notepad on Windows so Cursor/.md association is bypassed.
            try:
                import subprocess
                subprocess.Popen(["notepad.exe", str(path)])
            except Exception:
                try:
                    import os
                    os.startfile(path)  # type: ignore[attr-defined]
                except Exception:
                    webbrowser.open(path.as_uri())

        ttk.Button(bar, text="Abrir pasta", command=open_folder).pack(
            side="right", padx=(4, 0)
        )
        ttk.Button(bar, text="Abrir no Bloco de notas", command=open_external).pack(
            side="right"
        )
        ttk.Button(bar, text="Fechar", command=win.destroy).pack(
            side="right", padx=(0, 8)
        )
        body = scrolledtext.ScrolledText(win, wrap="word", font=("Consolas", 10))
        body.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        try:
            body.insert("1.0", path.read_text(encoding="utf-8"))
        except OSError as exc:
            body.insert("1.0", f"(erro a ler ficheiro: {exc})")
        body.configure(state="disabled")

    def _onto_ili_refresh(self):
        """Reload Onto→ILI proposals into the listbox."""
        self.onto_ili_list.delete(0, "end")
        self._onto_ili_rows = []
        ws = self._ws()
        if not ws:
            self.onto_ili_status.configure(text="(sem classe)")
            return
        try:
            from semantic.onto_ili import list_proposals
            # Prefer existing rows; do not auto-repropose on every refresh.
            rows = list_proposals(ws.class_id)
            if not rows:
                self.onto_ili_status.configure(
                    text="0 propostas — clique «Propor» após pesquisas Onto/PULO"
                )
                return
            # Show proposed first, then accepted, then rejected
            order = {"proposed": 0, "accepted": 1, "rejected": 2}
            rows.sort(
                key=lambda r: (
                    order.get(r.get("status") or "", 9),
                    -float(r.get("score") or 0),
                )
            )
            n_prop = sum(1 for r in rows if r.get("status") == "proposed")
            n_acc = sum(1 for r in rows if r.get("status") == "accepted")
            self.onto_ili_status.configure(
                text=f"{len(rows)} links · {n_prop} proposed · {n_acc} accepted"
            )
            for r in rows[:200]:
                st = (r.get("status") or "?")[:8]
                sc = float(r.get("score") or 0)
                line = (
                    f"[{st:8}] {sc:0.2f}  {r.get('onto_key')}  →  {r.get('ili')}"
                )
                self.onto_ili_list.insert("end", line)
                self._onto_ili_rows.append(r)
        except Exception as exc:  # noqa: BLE001
            self.onto_ili_status.configure(text=f"erro: {exc}")

    def _onto_ili_selected(self) -> Optional[dict]:
        sel = self.onto_ili_list.curselection()
        if not sel:
            messagebox.showinfo(APP, "Seleccione uma proposta na lista.")
            return None
        idx = int(sel[0])
        if idx < 0 or idx >= len(self._onto_ili_rows):
            return None
        return self._onto_ili_rows[idx]

    def _onto_ili_propose(self):
        ws = self._ws()
        if not ws:
            return
        self.status_var.set("Onto→ILI: a propor…")
        try:
            from semantic.onto_ili import propose_for_class
            from semantic.sense_index import SenseIndex, ingest_class_exports
            with SenseIndex() as si:
                ingest_class_exports(ws.class_id, index=si)
                rep = propose_for_class(ws.class_id, index=si)
            auto_n = (rep.get("auto_accept") or {}).get("n") or 0
            self._log(
                f"Onto→ILI propose: {rep.get('n_proposals')} proposals · "
                f"{rep.get('n_accepted')} accepted "
                f"(auto={auto_n})\n"
            )
            self._onto_ili_refresh()
            self.status_var.set("Onto→ILI: propostas actualizadas.")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(APP, str(exc))
            self.status_var.set("Onto→ILI propose failed.")

    def _onto_ili_accept(self):
        row = self._onto_ili_selected()
        ws = self._ws()
        if not row or not ws:
            return
        try:
            from semantic.onto_ili import set_proposal_status
            out = set_proposal_status(
                ws.class_id, row["onto_key"], row["ili"], "accepted",
            )
            self._log(f"Onto→ILI accepted: {out}\n")
            self._onto_ili_refresh()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(APP, str(exc))

    def _onto_ili_reject(self):
        row = self._onto_ili_selected()
        ws = self._ws()
        if not row or not ws:
            return
        try:
            from semantic.onto_ili import set_proposal_status
            out = set_proposal_status(
                ws.class_id, row["onto_key"], row["ili"], "rejected",
            )
            self._log(f"Onto→ILI rejected: {out}\n")
            self._onto_ili_refresh()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(APP, str(exc))

    def _onto_ili_accept_top(self):
        ws = self._ws()
        if not ws:
            return
        try:
            from semantic.onto_ili import accept_top
            out = accept_top(ws.class_id, n=5, min_score=0.6)
            self._log(f"Onto→ILI accept-top: {out}\n")
            self._onto_ili_refresh()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(APP, str(exc))

    def _log(self, text: str):
        self.log.insert("end", text)
        self.log.see("end")

    def _log_clear(self):
        self.log.delete("1.0", "end")


def main():
    # sanity-check config early
    try:
        load_config()
    except Exception as exc:  # noqa: BLE001
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(APP, f"config.json problem:\n{exc}")
        return 1
    CLASSES_DIR.mkdir(parents=True, exist_ok=True)
    app = Workbench()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
