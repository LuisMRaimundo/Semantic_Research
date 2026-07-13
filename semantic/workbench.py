#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Single-screen Fase 0 workbench: search → decide → run → concordance."""

from __future__ import annotations

import json
import sys
import threading
import webbrowser
from pathlib import Path
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
DECISION_CHOICES_PULO = ("", "UF", "RT", "exclude", "atributo", "contraste")
DECISION_CHOICES_ONTO = ("", "UF", "RT", "exclude", "contraste")
DECISION_LABELS = {
    "": "—",
    "UF": "UF",
    "RT": "RT",
    "exclude": "exclude",
    "atributo": "atributo",
    "contraste": "contraste",
}

GUIDE_TEXT = """\
SEMANTIC RESEARCH — QUICK GUIDE
════════════════════════════════

Daily path (3 steps)
────────────────────
1 · SEARCH
   Pick a class. Search a Portuguese lemma in PULO (ILI-anchored,
   sense-disambiguated) and/or Onto.PT (broader, fuzzy).
   Each synset becomes a sense card on the left.

2 · DECIDE
   For every sense, choose one label (see Glossary).
   Options differ by source:
     PULO  → — UF RT exclude atributo contraste
     Onto  → — UF RT exclude contraste   (no atributo)
   Fill meta: pref_label (preferred lemma) and axis (the property
   that defines the class, e.g. “invariance along a parameter”).
   Click Save decisions.

3 · RUN
   ▶ Run pipeline compiles your choices, runs the PULO / Onto
   engines, then LexWarrant (cross-source concordance).
   Read FINAL_RESULTS/<Class>.concordance.md — that is the deliverable
   (Onto.PT + PULO). Scratch files stay in out/ / results/.
   Resolve the “worklist” (divergences) by hand; the tool never
   auto-promotes a term.


What each source is for
───────────────────────
• PULO     — Portuguese WordNet; 1 synset = 1 sense; linked to ILI
             (Interlingual Index). Prefer this as the sense anchor.
• Onto.PT  — Larger Portuguese lexical net (incl. CONTO.PT weights).
             Corroborates / extends; synsets have no ILI.
• LexWarrant — Relator only: joins results by ILI (or weakly by term).
             Reports agreement / divergence; does not decide.


Glossary — decision labels
──────────────────────────
UF          Used For / “é mesmo isto”
            The sense IS the class meaning (or a true synonym).
            Maps to SKOS altLabel (alternative lexical form of the
            preferred concept). Example: invariável for TexturaUniforme.

RT          Related Term / “parecido”
            Related but not identical — useful neighbour, not a
            synonym. Maps to skos:related.
            Example: periódico when the axis is invariance, not period.

exclude     “não interessa”
            Wrong sense / wrong domain. Dropped from the class.
            Example: uniforme = military uniform.

atributo    Quality noun (attribute bucket) — PULO only
            A noun naming the quality, not an adjective for the
            texture itself (e.g. uniformidade, invariância).
            Maps to a distinct :temAtributo link — never altLabel.
            Onto.PT has no atributo: use UF (or exclude) there.

contraste   Contrast / opposite pole
            Opposes the class on the same axis (e.g. variável,
            desigual). Maps to :contrastaCom + scopeNote —
            never skos:related.
            Available on both PULO and Onto.PT.

—           (blank)
            Not decided yet. Pipeline will refuse incomplete senses
            when compiling a full run; mark every card before Run.


Glossary — other terms
──────────────────────
class / class_id
            One textural (or conceptual) category you are grounding
            lexically, e.g. TexturaUniforme.

pref_label  Preferred lemma for the class (display / SKOS prefLabel).

axis        Defining property used in adjudication tests
            (what must stay true for UF).

sense / synset
            One meaning: a set of synonyms + gloss. Decisions are
            per sense, not per spelling.

ILI         Interlingual Index (ili-30-…): shared concept id across
            wordnets. Primary join key in LexWarrant.

lemma       Dictionary form of a word (uniforme, not uniformes).

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
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="Class").pack(side="left")
        self.class_combo = ttk.Combobox(top, textvariable=self.class_var, width=28)
        self.class_combo.pack(side="left", padx=6)
        self.class_combo.bind("<<ComboboxSelected>>", lambda e: self._load_class())
        ttk.Button(top, text="New…", command=self._new_class).pack(side="left")
        ttk.Button(top, text="Open folder", command=self._open_folder).pack(
            side="left", padx=4
        )
        ttk.Button(top, text="↻", width=3, command=self._load_class).pack(side="left")
        ttk.Button(top, text="? Guide", command=self._open_guide).pack(
            side="right"
        )

        search = ttk.LabelFrame(self, text="1 · Search  (pick ONE lexicon)", padding=8)
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
        ).pack(side="left", padx=(8, 12))
        ttk.Entry(search, textvariable=self.query_var, width=32).pack(side="left")
        ttk.Combobox(search, textvariable=self.mode_var, width=12,
                     values=("Starts with", "Contains", "Exact"),
                     state="readonly").pack(side="left", padx=6)
        ttk.Button(search, text="Search", command=self._search).pack(side="left")

        mid = ttk.Panedwindow(self, orient="horizontal")
        mid.pack(fill="both", expand=True, padx=10, pady=4)

        left = ttk.Frame(mid)
        right = ttk.LabelFrame(
            mid, text="3 · Run  →  FINAL_RESULTS (Onto + PULO)", padding=6
        )
        mid.add(left, weight=3)
        mid.add(right, weight=2)

        filt = ttk.LabelFrame(left, text="2 · Decide — show cards from", padding=6)
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
            filt, text="Both", variable=self.filter_var, value="all",
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
        ttk.Button(btnrow, text="Save decisions", command=self._save_decisions).pack(
            side="left"
        )
        ttk.Button(btnrow, text="? Guide", command=self._open_guide).pack(
            side="left", padx=8
        )

        ttk.Label(right, text="Meta (axis / pref label)", font=("", 9, "bold")).pack(
            anchor="w"
        )
        self.meta_box = scrolledtext.ScrolledText(right, height=5, wrap="word")
        self.meta_box.pack(fill="x", pady=(0, 6))

        runrow = ttk.Frame(right)
        runrow.pack(fill="x")
        ttk.Button(runrow, text="▶ Run pipeline", command=self._run).pack(side="left")
        ttk.Button(
            runrow, text="Open FINAL RESULTS",
            command=self._open_final_results,
        ).pack(side="left", padx=6)
        ttk.Button(
            runrow, text="Open concordance",
            command=self._open_concordance,
        ).pack(side="left")

        self.final_banner = tk.Label(
            right,
            text="Deliverable folder:  FINAL_RESULTS/  (Onto.PT + PULO concordance)",
            bg="#1B5E20", fg="white", font=("", 9, "bold"),
            anchor="w", padx=8, pady=4,
        )
        self.final_banner.pack(fill="x", pady=(8, 0))

        self.log = scrolledtext.ScrolledText(right, height=20, wrap="word")
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
            "UF", "RT", "exclude", "atributo", "contraste",
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

        def ok():
            if not cid.get().strip():
                messagebox.showerror(APP, "class_id required")
                return
            ClassWorkspace.create(
                cid.get().strip(),
                pref_label=pref.get().strip(),
                axis=axis.get().strip(),
            )
            win.destroy()
            self._refresh_classes(select=cid.get().strip().replace(" ", ""))

        ttk.Button(win, text="Create", command=ok).grid(
            row=3, column=1, sticky="e", padx=8, pady=10
        )

    def _ws(self) -> ClassWorkspace | None:
        name = self.class_var.get().strip()
        if not name:
            return None
        try:
            return ClassWorkspace.open(name)
        except FileNotFoundError:
            return None

    def _load_class(self):
        ws = self._ws()
        if not ws:
            return
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
                text="Onto options:  —  UF  RT  exclude  contraste   (NO atributo)"
            )
        elif f == "pulo":
            self.decide_hint.configure(
                text="PULO options:  —  UF  RT  exclude  atributo  contraste"
            )
        else:
            self.decide_hint.configure(
                text="Both · blue=PULO (has atributo) · amber=Onto (no atributo)"
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
        if filt in ("pulo", "onto"):
            senses = [s for s in senses if (s.get("source") or "").lower() == filt]

        if not senses:
            msg = "No senses yet. Search a Portuguese lemma above."
            if filt == "pulo":
                msg = "No PULO cards. Search with «PULO — ILI» selected."
            elif filt == "onto":
                msg = "No Onto.PT cards. Search with «Onto.PT» selected."
            tk.Label(
                self.sense_frame, text=msg, fg="#555", anchor="w", justify="left"
            ).pack(anchor="w", padx=8, pady=12)
            return

        for s in senses:
            sk = decmod.sense_key(s["source"], s["key"])
            src = (s.get("source") or "").lower()
            if src == "onto":
                bg, accent, banner = "#FFF6E5", "#8A5A00", (
                    "Onto.PT  ·  fuzzy coverage  ·  options: UF · RT · exclude · contraste"
                )
                key_line = f"id: {s.get('key')}"
            else:
                bg, accent, banner = "#E8F1FB", "#0B3D6E", (
                    "PULO  ·  ILI anchor  ·  options: UF · RT · exclude · atributo · contraste"
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

            choice_set = self._choices_for(src)
            raw = s.get("decision") or ""
            if src == "onto" and raw == "atributo":
                raw = "UF"
            var = tk.StringVar(value=raw if raw in choice_set else "")
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
        for s in dec.get("senses", []):
            sk = decmod.sense_key(s["source"], s["key"])
            if sk in self._sense_vars:
                s["decision"] = self._sense_vars[sk].get()
        decmod.save_decisions(ws.decisions_json, dec)
        self.status_var.set("Decisions saved.")
        self._load_class()

    # -- search / run ----------------------------------------------------
    def _search(self):
        ws = self._ws()
        q = self.query_var.get().strip()
        if not ws or not q:
            messagebox.showinfo(APP, "Pick a class and type a query.")
            return
        self.status_var.set("Searching…")

        def work():
            try:
                info = search_and_seed(
                    ws.class_id, q, source=self.source_var.get(),
                    mode=self.mode_var.get(),
                )
                self.after(0, lambda: self._search_done(info, None))
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda: self._search_done(None, exc))

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
        self._load_class()

    def _run(self):
        ws = self._ws()
        if not ws:
            return
        self._save_decisions()
        self.status_var.set("Running pipeline…")
        self._log("\n▶ Running…\n")

        def work():
            try:
                summary = run_class(ws.class_id)
                self.after(0, lambda: self._run_done(summary, None))
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda: self._run_done(None, exc))

        threading.Thread(target=work, daemon=True).start()

    def _run_done(self, summary, err):
        if err:
            messagebox.showerror(APP, str(err))
            self.status_var.set("Run failed.")
            return
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
        ws = self._ws()
        if not ws:
            return
        path = ws.concordance_md()
        if not path.exists():
            messagebox.showinfo(
                APP,
                "No FINAL_RESULTS concordance yet — Run the pipeline first.",
            )
            return
        try:
            import os
            os.startfile(path)  # type: ignore[attr-defined]
        except Exception:
            webbrowser.open(path.as_uri())

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
