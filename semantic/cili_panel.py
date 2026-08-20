"""Tk CILI panel — additive Toplevel; does not restructure the workbench."""

from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any, Callable, Optional

from engines.CILI.cili_engine import CiliEngine, canonical_ili


def sense_ili(sense: dict[str, Any]) -> Optional[str]:
    for fld in ("cili_id", "cili", "to_ili", "ili"):
        cid = canonical_ili(sense.get(fld))
        if cid:
            return cid
    return None


class CiliPanel(tk.Toplevel):
    def __init__(
        self,
        master: tk.Misc,
        *,
        class_root: Path | None = None,
        on_status: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(master)
        self.title("CILI — lexicographical reference")
        self.geometry("980x640")
        self.transient(master)
        self.class_root = class_root
        self.on_status = on_status or (lambda _s: None)
        self.engine = CiliEngine.from_config()
        self._results: list[dict[str, Any]] = []

        bar = ttk.Frame(self, padding=(8, 6))
        bar.pack(fill="x")
        self.q_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="any")
        self.pos_var = tk.StringVar(value="")
        self.lang_var = tk.StringVar(value="")
        ttk.Entry(bar, textvariable=self.q_var, width=36).pack(side="left")
        ttk.Combobox(
            bar, textvariable=self.mode_var, width=12, state="readonly",
            values=("any", "lemma", "definition"),
        ).pack(side="left", padx=4)
        ttk.Combobox(
            bar, textvariable=self.pos_var, width=8, state="readonly",
            values=("", "n", "v", "a", "r", "s"),
        ).pack(side="left", padx=4)
        ttk.Entry(bar, textvariable=self.lang_var, width=6).pack(side="left", padx=4)
        ttk.Button(bar, text="Search", command=self._search).pack(side="left", padx=4)
        ttk.Button(bar, text="Entry", command=self._entry).pack(side="left")
        ttk.Button(bar, text="Copy as candidate", command=self._copy_candidate).pack(
            side="left", padx=8
        )
        ttk.Label(
            bar, text="read-only · does not write decisions", foreground="#666",
        ).pack(side="left", padx=8)

        mid = ttk.Panedwindow(self, orient="horizontal")
        mid.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        left = ttk.Frame(mid)
        right = ttk.Frame(mid)
        mid.add(left, weight=1)
        mid.add(right, weight=2)
        self.listbox = tk.Listbox(left, font=("Consolas", 9))
        self.listbox.pack(fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        self.detail = tk.Text(right, wrap="word", font=("Georgia", 10), height=20)
        self.detail.pack(fill="both", expand=True)
        self.detail.tag_configure("ili", foreground="#7a3b2e", font=("Consolas", 10, "bold"))
        self.detail.tag_configure("lemma", foreground="#7a3b2e", underline=True)
        self.detail.bind("<Button-1>", self._on_detail_click)
        self._lemma_spans: list[tuple[str, str]] = []

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind("<Escape>", lambda _e: self.destroy())
        self.bind("<Return>", lambda _e: self._search())
        if not self.engine.index_path.exists():
            self._set_detail(
                "CILI index missing. Run:\n  python sr.py cili index"
            )

    def open_concept(self, ili: str) -> None:
        cid = canonical_ili(ili)
        if not cid:
            return
        self._show_concept(cid)
        self.lift()
        self.focus_force()

    def open_entry(self, lemma: str) -> None:
        self.q_var.set(lemma)
        self._entry()
        self.lift()
        self.focus_force()

    def _set_detail(self, text: str) -> None:
        self.detail.configure(state="normal")
        self.detail.delete("1.0", "end")
        self.detail.insert("1.0", text)
        self.detail.configure(state="disabled")
        self._lemma_spans = []

    def _search(self) -> None:
        q = self.q_var.get().strip()
        if not q:
            return
        try:
            doc = self.engine.search(
                q,
                mode=self.mode_var.get() or "any",
                pos=self.pos_var.get() or "",
                lang=self.lang_var.get().strip() or "",
                limit=80,
            )
        except FileNotFoundError as exc:
            self._set_detail(str(exc))
            return
        self._results = doc.get("results") or []
        self.listbox.delete(0, "end")
        for r in self._results:
            self.listbox.insert(
                "end",
                f"{r['ili']}  {r.get('pos') or ''}  "
                f"{(r.get('definition') or '')[:70]}",
            )
        self.on_status(f"CILI: {doc.get('total', 0)} matches")
        if self._results:
            self.listbox.selection_set(0)
            self._show_concept(self._results[0]["ili"])

    def _entry(self) -> None:
        lemma = self.q_var.get().strip()
        if not lemma:
            return
        try:
            e = self.engine.entry(lemma)
        except FileNotFoundError as exc:
            self._set_detail(str(exc))
            return
        self._show_entry(e)

    def _on_select(self, _evt=None) -> None:
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = int(sel[0])
        if 0 <= idx < len(self._results):
            self._show_concept(self._results[idx]["ili"])

    def _show_concept(self, ili: str) -> None:
        c = self.engine.concept(ili)
        if not c:
            self._set_detail(f"{ili} not found")
            return
        lines = [
            f"{c['ili']}  {c.get('kind')}  {c.get('pos_name')}  "
            f"pos_norm={c.get('pos_norm')}  {c.get('status')}",
            "",
            c.get("definition") or "(no definition)",
            "",
            f"RDF  {c.get('rdf_uri')}",
            f"page {c.get('page_uri')}",
            "",
        ]
        for lg, lems in (c.get("by_lang") or {}).items():
            lines.append(f"{lg}: {', '.join(lems)}")
        lines.append("")
        lines.append("mappings")
        for m in c.get("mappings") or []:
            lines.append(
                f"  {m.get('resource')}  {m.get('target')}  {m.get('lemmas') or ''}"
            )
        self._set_detail("\n".join(lines))
        self._current = c

    def _show_entry(self, e: dict[str, Any]) -> None:
        if not e.get("count"):
            self._set_detail(
                f"No exact lemma {e.get('lemma')!r}. Try Search."
            )
            return
        lines = [
            f"{e['lemma']}  ·  {e['count']} sense(s)  ·  {', '.join(e.get('langs') or [])}",
            "",
            "equivalents",
        ]
        for lg, rows in (e.get("equivalents") or {}).items():
            bits = [f"{r['lemma']}^{r['shared_senses']}" for r in rows]
            lines.append(f"  {lg}: {', '.join(bits)}")
        for pos, rows in (e.get("groups") or {}).items():
            lines.append("")
            lines.append(pos)
            for i, r in enumerate(rows, 1):
                extra = r.get("pos_name") or ""
                lines.append(
                    f"  {i}. {r.get('definition')}  {r['ili']}  [{extra}]"
                )
                for lg, lems in (r.get("translations") or {}).items():
                    lines.append(f"     {lg}: {', '.join(lems)}")
        self._set_detail("\n".join(lines))
        self._current = {"entry": e, "ili": None}

    def _on_detail_click(self, _evt=None) -> None:
        # Pivot: if the selection looks like an ili or a single lemma, open it.
        try:
            sel = self.detail.get("sel.first", "sel.last").strip()
        except tk.TclError:
            return
        cid = canonical_ili(sel)
        if cid:
            self.open_concept(cid)
            return
        if sel and " " not in sel and len(sel) < 40:
            self.open_entry(sel)

    def _copy_candidate(self) -> None:
        cur = getattr(self, "_current", None)
        if not isinstance(cur, dict) or not cur.get("ili"):
            messagebox.showinfo(
                "CILI", "Open a concept first, then copy as candidate."
            )
            return
        snippet = {
            "ili": cur["ili"],
            "definition": cur.get("definition") or "",
            "lemmas": cur.get("by_lang") or {},
            "rdf_uri": cur.get("rdf_uri"),
            "page_uri": cur.get("page_uri"),
            "note": "candidate only — not a decision; paste/adjudicate manually",
        }
        text = json.dumps(snippet, ensure_ascii=False, indent=2)
        self.clipboard_clear()
        self.clipboard_append(text)
        if self.class_root is not None:
            dest_dir = Path(self.class_root) / "_specs"
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / "cili_candidate.json"
            dest.write_text(text + "\n", encoding="utf-8")
            self.on_status(f"CILI candidate → clipboard + {dest}")
        else:
            self.on_status("CILI candidate → clipboard (no class open)")


def inline_definition(engine: CiliEngine | None, ili: str) -> str:
    cid = canonical_ili(ili)
    if not cid or engine is None:
        return ""
    try:
        c = engine.concept(cid)
    except Exception:  # noqa: BLE001
        return ""
    if not c:
        return ""
    return (c.get("definition") or "").strip()
