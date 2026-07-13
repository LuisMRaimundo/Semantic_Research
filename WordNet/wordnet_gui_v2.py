#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordNet GUI Completo (Open English Wordnet) – Integração de TODAS as funcionalidades
Inclui: synsets, relações, similaridade, multilíngue, IC, navegação hierárquica,
        morphy, domínios, visualização de grafos, etc.

Lexicon: Open English Wordnet (globalwordnet/english-wordnet)
         https://github.com/globalwordnet/english-wordnet

Requisitos:
    pip install wn nltk pandas matplotlib networkx

Primeira execução: o script descarrega automaticamente o Open English Wordnet.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog
from typing import List, Dict, Any, Optional, Tuple
import csv
import json
from collections import defaultdict
from pathlib import Path as _Path

WORDNET_HOME = _Path(__file__).resolve().parent
EXPORTS_DIR = WORDNET_HOME / "exports"


def ensure_exports_dir() -> _Path:
    """Local WordNet deliverable folder (not the shared Hub Exports)."""
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return EXPORTS_DIR


def _safe_export_slug(term: str) -> str:
    raw = (term or "export").strip().replace(" ", "_")
    cleaned = "".join(c for c in raw if c.isalnum() or c in ("_", "-", "."))
    return cleaned or "export"


# Shared ecosystem settings (optional — WordNet prefers its own exports/).
try:
    sys.path.insert(0, str(WORDNET_HOME.parent))
    import ecosys_settings
except Exception:  # noqa: BLE001
    ecosys_settings = None

# --- Open English Wordnet (wn library) ---
try:
    import oewn_backend as wn
    from oewn_backend import (
        WordNetLemmatizer,
        ensure_oewn,
        ensure_translation_lexicon,
        format_score,
        get_available_languages,
        information_content_value,
        wordnet_ic,
    )

    ensure_oewn()
    test_synsets = wn.synsets('test')
    if not test_synsets:
        raise Exception("Open English Wordnet não está funcionando corretamente")

except Exception as e:
    print(f"Configurando Open English Wordnet pela primeira vez... ({e})")
    try:
        import oewn_backend as wn
        from oewn_backend import (
            WordNetLemmatizer,
            ensure_oewn,
            get_available_languages,
            information_content_value,
            wordnet_ic,
        )
        ensure_oewn()
    except Exception:
        messagebox.showerror(
            "Erro Fatal",
            "Open English Wordnet não está instalado corretamente.\n\n"
            "Execute no terminal:\n"
            "pip install wn nltk\n"
            "python -c \"import wn; wn.download('oewn:2024')\"",
        )
        sys.exit(1)

# --- Para visualização de grafos ---
try:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    import networkx as nx
    HAS_GRAPH = True
except Exception:
    HAS_GRAPH = False

# Garantir recursos
def _ensure_wordnet():
    """Garante que o Open English Wordnet está disponível."""
    print("Verificando Open English Wordnet...")
    lexicon = ensure_oewn()
    print(f"✓ {lexicon} disponível")
    try:
        import nltk
        nltk.download('brown', quiet=True)
        print("✓ corpus Brown disponível (Information Content)")
    except Exception:
        print("✗ corpus Brown indisponível (métricas IC podem falhar)")

_ensure_wordnet()

# Obter idiomas disponíveis
AVAILABLE_LANGUAGES = get_available_languages()
print(f"\nIdiomas disponíveis: {len(AVAILABLE_LANGUAGES)}")
print("  (* = léxico de tradução descarrega na primeira pesquisa nesse idioma)")
for code, name in AVAILABLE_LANGUAGES.items():
    print(f"  • {name} ({code})")

# ---------- Constantes e Mapeamentos ----------
POS_MAP = {
    "Todas": None,
    "Substantivo (n)": wn.NOUN,
    "Verbo (v)": wn.VERB,
    "Adjetivo (a)": wn.ADJ,
    "Advérbio (r)": wn.ADV,
}

SIMILARITY_METRICS = [
    "path_similarity",
    "lch_similarity", 
    "wup_similarity",
    "res_similarity",
    "jcn_similarity",
    "lin_similarity"
]

IC_CORPORA = {
    "Brown": "ic-brown.dat",
    "SemCor": "ic-semcor.dat",
    "SemCor (add1)": "ic-semcor-add1.dat",
    "Brown (add1)": "ic-brown-add1.dat",
    "Brown (resnik)": "ic-brown-resnik-add1.dat",
    "SemCor (resnik)": "ic-semcor-resnik-add1.dat"
}

# Use idiomas realmente disponíveis
LANGUAGES = {name: code for code, name in AVAILABLE_LANGUAGES.items()}

# ---------- Funções Utilitárias ----------
def _safe_call(func, *args, default=None, **kwargs):
    """Executa função com tratamento de erros"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return default if default is not None else str(e)

def _format_list(items, max_items=20):
    """Formata lista para exibição"""
    if not items:
        return "—"
    if len(items) > max_items:
        return f"{', '.join(str(i) for i in items[:max_items])}... (+{len(items)-max_items})"
    return ', '.join(str(i) for i in items)

def _get_ic():
    """Obtém Information Content (Brown corpus; primeira chamada pode demorar ~1–2 min)."""
    try:
        return wordnet_ic.ic("ic-brown.dat")
    except Exception:
        return None

def _show_help_window(parent, title, text):
    """Open a scrollable, read-only quick-reference window."""
    win = tk.Toplevel(parent)
    win.title(title)
    win.geometry("800x660")
    win.transient(parent)

    bar = ttk.Frame(win, padding=(10, 8))
    bar.pack(side="bottom", fill="x")
    ttk.Button(bar, text="Fechar", command=win.destroy).pack(side="right")

    frame = ttk.Frame(win, padding=(10, 10))
    frame.pack(fill="both", expand=True)
    txt = tk.Text(frame, wrap="word", relief="flat", padx=10, pady=8,
                  font=("Segoe UI", 10))
    vsb = ttk.Scrollbar(frame, orient="vertical", command=txt.yview)
    txt.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    txt.pack(side="left", fill="both", expand=True)
    txt.insert("1.0", text)
    txt.configure(state="disabled")
    win.bind("<Escape>", lambda _e: win.destroy())


# ---------- Classe Principal do GUI ----------
class WordNetCompleteGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Open English Wordnet — Interface Completa")
        self.geometry("1200x800")
        
        # Estado
        self.current_synsets = []
        self.ic = None
        self.lemmatizer = None
        self._ic_loading = False
        self._graph_fig = None
        self._graph_canvas = None
        
        try:
            self.lemmatizer = WordNetLemmatizer()
        except Exception:
            print("⚠ WordNetLemmatizer não disponível")
        
        # Criar interface
        ensure_exports_dir()
        self._build_ui()
        self._set_status(
            f"Pronto. Exportações → {EXPORTS_DIR}  "
            "(IC em segundo plano ~1–2 min)."
        )
        # wn uses SQLite — must run on the main Tk thread, not a worker thread.
        self.after(300, self._preload_ic_on_main_thread)
        
    def _build_ui(self):
        """Constrói a interface com abas"""
        # Frame superior para busca
        search_frame = ttk.Frame(self, padding=5)
        search_frame.pack(fill="x")
        
        ttk.Label(search_frame, text="Termo:").grid(row=0, column=0, sticky="w")
        self.term_var = tk.StringVar()
        term_entry = ttk.Entry(search_frame, textvariable=self.term_var, width=30)
        term_entry.grid(row=0, column=1, padx=5)
        term_entry.bind('<Return>', lambda e: self.on_search())
        
        ttk.Label(search_frame, text="POS:").grid(row=0, column=2)
        self.pos_var = tk.StringVar(value="Todas")
        ttk.Combobox(search_frame, textvariable=self.pos_var, 
                    values=list(POS_MAP.keys()), width=15, state="readonly").grid(row=0, column=3, padx=5)
        
        ttk.Label(search_frame, text="Idioma:").grid(row=0, column=4)
        self.lang_var = tk.StringVar(value="English")
        ttk.Combobox(search_frame, textvariable=self.lang_var,
                    values=list(LANGUAGES.keys()), width=15, state="readonly").grid(row=0, column=5, padx=5)
        
        ttk.Button(search_frame, text="🔍 Pesquisar", command=self.on_search).grid(row=0, column=6, padx=5)
        ttk.Button(search_frame, text="💾 Exportar…", command=self.export_all).grid(
            row=0, column=7, padx=(5, 2)
        )
        ttk.Button(
            search_frame,
            text="💾→ exports/",
            command=self.export_all_to_exports,
        ).grid(row=0, column=8, padx=2)
        ttk.Button(search_frame, text="📁 exports", command=self._open_exports_folder).grid(
            row=0, column=9, padx=2
        )
        ttk.Button(search_frame, text="❓ Ajuda", command=self._show_help).grid(
            row=0, column=10, padx=5
        )
        
        # Notebook com abas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Aba 1: Synsets e Relações
        self.tab_synsets = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_synsets, text="📚 Synsets & Relações")
        self._build_synsets_tab()
        
        # Aba 2: Similaridade
        self.tab_similarity = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_similarity, text="📊 Similaridade")
        self._build_similarity_tab()
        
        # Aba 3: Navegação Hierárquica
        self.tab_hierarchy = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_hierarchy, text="🌳 Hierarquia")
        self._build_hierarchy_tab()
        
        # Aba 4: Ferramentas Avançadas
        self.tab_advanced = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_advanced, text="🔧 Avançado")
        self._build_advanced_tab()
        
        # Aba 5: Visualização
        if HAS_GRAPH:
            self.tab_visual = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_visual, text="📈 Visualização")
            self._build_visual_tab()

        self.status_var = tk.StringVar(value="")
        ttk.Label(self, textvariable=self.status_var, anchor="w").pack(fill="x", padx=8, pady=(0, 4))

    def _set_status(self, message: str):
        self.status_var.set(message)

    def _preload_ic_on_main_thread(self):
        """Precalcula IC na thread principal (requisito do SQLite/wn)."""
        if wordnet_ic.is_ready():
            self.ic = wordnet_ic.ic()
            self._set_status("Information Content pronto (corpus Brown).")
            return
        self._set_status("A calcular Information Content (corpus Brown); aguarde ~1–2 min...")
        self.update_idletasks()
        try:
            self.ic = wordnet_ic.ic()
            self._set_status("Information Content pronto (corpus Brown).")
        except Exception as exc:
            print(f"⚠ IC preload falhou: {exc}")
            self._set_status("Information Content indisponível (verifique NLTK + corpus Brown).")
    
    HELP_TEXT = """GUIA RÁPIDO — Open English WordNet

O que é: um explorador da Open English WordNet (inglês), com tradução por ILI
para outras línguas (ex.: lemas em português). O IC (Information Content) é
calculado em segundo plano no arranque — pode demorar 1–2 min na 1.ª vez.

──────────────────────────────────────────────────────────────────────────
PASSO 1 — Pesquisar
──────────────────────────────────────────────────────────────────────────
  1. Escreva a palavra em «Termo».
  2. (Opcional) escolha «POS» (classe gramatical) e «Idioma».
  3. Clique «🔍 Pesquisar» (ou Enter).
  4. Percorra as abas para ver os resultados.

──────────────────────────────────────────────────────────────────────────
PASSO 2 — As abas
──────────────────────────────────────────────────────────────────────────
  • «Synsets e Relações»: acepções, definições, lemas (incl. PT via ILI) e
    relações (hiperónimos, hipónimos, merónimos, antónimos…).
  • «Similaridade»: carregue synsets e calcule métricas entre pares
    (path, wup, e — se o IC estiver pronto — Resnik/JCN/Lin, e LCH por par).
  • «Hierarquia»: caminhos de hiperonímia, raízes, profundidades e fechos.
  • «Avançado»: Morphy (lematização), Domínios, Frames de verbos, IC.
  • «Visualização»: «Gerar Grafo» desenha a rede de relações; ajuste
    «Vizinhos/relação». Use a barra de ferramentas para zoom/gravar.

──────────────────────────────────────────────────────────────────────────
PASSO 3 — Exportar  — TODAS as vertentes → pasta WordNet/exports/
──────────────────────────────────────────────────────────────────────────
  Exporta Synsets+relações, Similaridade, Hierarquia e Visualização.

  • «💾→ exports/» — grava TUDO de uma vez na pasta local
        WordNet/exports/<termo>_<data>/
        (facets.json + report.md + graph.png + CSV). Preferido.

  • «💾 Exportar…» — diálogo; pasta inicial = WordNet/exports/
        Escolha o formato pela extensão:
     • .result.json — ficheiro Fase 0 / LexWarrant (pede o nome da classe);
     • .json — facetas estruturadas (synsets, hierarquia, visualização…);
     • .md / .txt — relatório legível (+ .graph.png ao lado);
     • .csv — tabela de synsets (+ .similarity.csv);
     • .png — só a imagem do grafo.

  • «📁 exports» — abre a pasta WordNet/exports/ no Explorador.

──────────────────────────────────────────────────────────────────────────
A SEGUIR
──────────────────────────────────────────────────────────────────────────
  Grave em «.result.json» (o padrão) e carregue esse ficheiro no LexWarrant,
  ao lado do ONTO e da PULO. A WordNet entra como CORROBORAÇÃO (sinalização):
  não propõe UF/RT — confirma, pelo ILI/termo, o que o ONTO e a PULO admitem.
"""

    def _show_help(self):
        _show_help_window(self, "Ajuda — Open English WordNet", self.HELP_TEXT)

    def _build_synsets_tab(self):
        """Aba de synsets e relações"""
        # Frame com scroll
        canvas = tk.Canvas(self.tab_synsets)
        scrollbar = ttk.Scrollbar(self.tab_synsets, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Área de texto para resultados
        self.text_synsets = scrolledtext.ScrolledText(scrollable_frame, wrap="word", height=35, width=120)
        self.text_synsets.pack(fill="both", expand=True, padx=5, pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _build_similarity_tab(self):
        """Aba de métricas de similaridade"""
        frame = ttk.Frame(self.tab_similarity, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Inputs
        input_frame = ttk.LabelFrame(frame, text="Comparação de Termos", padding=10)
        input_frame.pack(fill="x", pady=5)
        
        ttk.Label(input_frame, text="Termo 1:").grid(row=0, column=0, sticky="w")
        self.sim_term1 = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.sim_term1, width=25).grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="Synset 1:").grid(row=0, column=2)
        self.sim_synset1 = ttk.Combobox(input_frame, width=30)
        self.sim_synset1.grid(row=0, column=3, padx=5)
        
        ttk.Label(input_frame, text="Termo 2:").grid(row=1, column=0, sticky="w")
        self.sim_term2 = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.sim_term2, width=25).grid(row=1, column=1, padx=5)
        
        ttk.Label(input_frame, text="Synset 2:").grid(row=1, column=2)
        self.sim_synset2 = ttk.Combobox(input_frame, width=30)
        self.sim_synset2.grid(row=1, column=3, padx=5)
        
        ttk.Button(input_frame, text="Carregar Synsets", 
                  command=self.load_synsets_for_similarity).grid(row=0, column=4, rowspan=2, padx=10)
        
        # IC Corpus selection
        ttk.Label(input_frame, text="IC Corpus:").grid(row=2, column=0, sticky="w")
        self.ic_corpus_var = tk.StringVar(value="Brown")
        ttk.Combobox(input_frame, textvariable=self.ic_corpus_var,
                    values=list(IC_CORPORA.keys()), width=20).grid(row=2, column=1, padx=5)
        
        ttk.Button(input_frame, text="Calcular Similaridades",
                  command=self.calculate_similarities).grid(row=2, column=3, padx=5)
        
        # Resultados
        results_frame = ttk.LabelFrame(frame, text="Resultados de Similaridade", padding=10)
        results_frame.pack(fill="both", expand=True, pady=5)
        
        self.text_similarity = scrolledtext.ScrolledText(results_frame, wrap="word", height=20)
        self.text_similarity.pack(fill="both", expand=True)
    
    def _build_hierarchy_tab(self):
        """Aba de navegação hierárquica"""
        frame = ttk.Frame(self.tab_hierarchy, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Controles
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill="x", pady=5)
        
        ttk.Label(control_frame, text="Synset:").pack(side="left", padx=5)
        self.hier_synset_var = tk.StringVar()
        self.hier_synset_combo = ttk.Combobox(control_frame, textvariable=self.hier_synset_var, width=30)
        self.hier_synset_combo.pack(side="left", padx=5)
        
        ttk.Button(control_frame, text="Explorar Hierarquia",
                  command=self.explore_hierarchy).pack(side="left", padx=5)
        
        ttk.Label(control_frame, text="Profundidade:").pack(side="left", padx=5)
        self.depth_var = tk.IntVar(value=3)
        ttk.Spinbox(control_frame, from_=1, to=10, textvariable=self.depth_var,
                   width=5).pack(side="left", padx=5)
        
        # Área de resultados
        self.text_hierarchy = scrolledtext.ScrolledText(frame, wrap="word", height=25)
        self.text_hierarchy.pack(fill="both", expand=True)
    
    def _build_advanced_tab(self):
        """Aba de ferramentas avançadas"""
        notebook_adv = ttk.Notebook(self.tab_advanced)
        notebook_adv.pack(fill="both", expand=True)
        
        # Sub-aba: Morphy
        morphy_frame = ttk.Frame(notebook_adv)
        notebook_adv.add(morphy_frame, text="Morphy")
        self._build_morphy_frame(morphy_frame)
        
        # Sub-aba: Domínios
        domains_frame = ttk.Frame(notebook_adv)
        notebook_adv.add(domains_frame, text="Domínios")
        self._build_domains_frame(domains_frame)
        
        # Sub-aba: Frames de Verbos
        frames_frame = ttk.Frame(notebook_adv)
        notebook_adv.add(frames_frame, text="Frames")
        self._build_frames_frame(frames_frame)
        
        # Sub-aba: Information Content
        ic_frame = ttk.Frame(notebook_adv)
        notebook_adv.add(ic_frame, text="Info Content")
        self._build_ic_frame(ic_frame)
    
    def _build_morphy_frame(self, parent):
        """Frame para análise morfológica"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Palavra para análise morfológica:").pack(anchor="w", pady=5)
        
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill="x", pady=5)
        
        self.morphy_input = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.morphy_input, width=30).pack(side="left", padx=5)
        ttk.Button(input_frame, text="Analisar", command=self.analyze_morphy).pack(side="left")
        
        self.text_morphy = scrolledtext.ScrolledText(frame, wrap="word", height=15)
        self.text_morphy.pack(fill="both", expand=True, pady=5)
    
    def _build_domains_frame(self, parent):
        """Frame para domínios semânticos"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Explorar domínios semânticos dos synsets carregados").pack(anchor="w", pady=5)
        
        ttk.Button(frame, text="Analisar Domínios", command=self.analyze_domains).pack(anchor="w", pady=5)
        
        self.text_domains = scrolledtext.ScrolledText(frame, wrap="word", height=20)
        self.text_domains.pack(fill="both", expand=True)
    
    def _build_frames_frame(self, parent):
        """Frame para frames de verbos"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Frames de sentença para verbos").pack(anchor="w", pady=5)
        
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill="x", pady=5)
        
        self.verb_input = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.verb_input, width=30).pack(side="left", padx=5)
        ttk.Button(input_frame, text="Buscar Frames", command=self.get_verb_frames).pack(side="left")
        
        self.text_frames = scrolledtext.ScrolledText(frame, wrap="word", height=20)
        self.text_frames.pack(fill="both", expand=True)
    
    def _build_ic_frame(self, parent):
        """Frame para Information Content"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Análise de Information Content").pack(anchor="w", pady=5)
        
        ttk.Button(frame, text="Calcular IC dos Synsets", command=self.calculate_ic).pack(anchor="w", pady=5)
        
        self.text_ic = scrolledtext.ScrolledText(frame, wrap="word", height=20)
        self.text_ic.pack(fill="both", expand=True)
    
    def _build_visual_tab(self):
        """Aba de visualização de grafos"""
        if not HAS_GRAPH:
            ttk.Label(self.tab_visual, text="Matplotlib/NetworkX não instalado").pack()
            return
            
        frame = ttk.Frame(self.tab_visual, padding=5)
        frame.pack(fill="both", expand=True)
        
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill="x", pady=5)
        
        ttk.Label(control_frame, text="Tipo de Grafo:").pack(side="left", padx=5)
        self.graph_type = tk.StringVar(value="Todos")
        ttk.Combobox(control_frame, textvariable=self.graph_type,
                    values=["Hiperônimos", "Hipônimos", "Similares", "Todos"],
                    width=15, state="readonly").pack(side="left", padx=5)

        ttk.Label(control_frame, text="Vizinhos/relação:").pack(side="left", padx=(12, 2))
        self.graph_neighbors = tk.IntVar(value=4)
        ttk.Spinbox(control_frame, from_=1, to=10, textvariable=self.graph_neighbors,
                    width=4).pack(side="left")

        ttk.Button(control_frame, text="Gerar Grafo", command=self.generate_graph).pack(side="left", padx=10)

        # Canvas para o grafo
        self.graph_frame = ttk.Frame(frame)
        self.graph_frame.pack(fill="both", expand=True)
        ttk.Label(
            self.graph_frame,
            text="Pesquise um termo e clique em «Gerar Grafo».\n"
                 "Nós cor-de-laranja = synsets pesquisados; azuis = relacionados.",
            justify="center", foreground="#666",
        ).pack(pady=40)
    
    # ---------- Funções de Busca e Processamento ----------
    
    def on_search(self):
        """Busca principal por termo"""
        term = self.term_var.get().strip()
        if not term:
            messagebox.showinfo("Aviso", "Digite um termo para pesquisar")
            return
        
        pos = POS_MAP.get(self.pos_var.get())
        lang_code = LANGUAGES.get(self.lang_var.get(), 'eng')
        
        try:
            if lang_code != "eng":
                self._set_status(f"A preparar léxico {self.lang_var.get()}...")
                ensure_translation_lexicon(lang_code)
                AVAILABLE_LANGUAGES.update(get_available_languages())
                LANGUAGES.update({name: code for code, name in AVAILABLE_LANGUAGES.items()})

            self.current_synsets = wn.synsets(term, pos=pos, lang=lang_code)
            self._set_status(
                f"{len(self.current_synsets)} synset(s) para '{term}' ({self.lang_var.get()})."
            )
            
            # Verificar resultados
            if not self.current_synsets:
                self.text_synsets.delete("1.0", "end")
                msg = f"📭 Nenhum synset encontrado para '{term}'"
                if self.lang_var.get() != "English":
                    msg += f" em {self.lang_var.get()}"
                msg += "\n\n💡 Sugestões:\n"
                msg += "• Verifique a ortografia\n"
                msg += "• Tente o singular/plural\n"
                msg += "• Use a forma base do verbo\n"
                msg += "• Tente em inglês primeiro\n"
                
                # Tentar formas relacionadas
                suggestions = []
                for p in [wn.NOUN, wn.VERB, wn.ADJ, wn.ADV]:
                    morph = wn.morphy(term, pos=p)
                    if morph and morph != term:
                        suggestions.append(morph)
                
                if suggestions:
                    msg += f"\n🔍 Você quis dizer: {', '.join(set(suggestions))}?"
                
                self.text_synsets.insert("1.0", msg)
                return
            
            # Exibir resultados
            self.display_synsets()
            
            # Atualizar combos em outras abas
            synset_names = [s.name() for s in self.current_synsets]
            self.hier_synset_combo['values'] = synset_names
            if synset_names:
                self.hier_synset_var.set(synset_names[0])
            
        except Exception as e:
            self.text_synsets.delete("1.0", "end")
            error_msg = f"❌ Erro na busca: {str(e)}\n\n"
            error_msg += "🔧 Debug Info:\n"
            error_msg += f"• Termo: '{term}'\n"
            error_msg += f"• POS: {pos}\n"
            error_msg += f"• Idioma: {lang_code}\n\n"
            error_msg += "💡 Possíveis soluções:\n"
            error_msg += "1. Reinicie o programa\n"
            error_msg += "2. Verifique se o Open English Wordnet está instalado:\n"
            error_msg += "   pip install wn\n"
            error_msg += "   python -c \"import wn; wn.download('oewn:2024')\"\n"
            error_msg += "3. Tente com uma palavra simples como 'dog' ou 'run'\n"
            self.text_synsets.insert("1.0", error_msg)
            
            # Log do erro
            print(f"Erro detalhado: {e}")
            import traceback
            traceback.print_exc()
    
    def display_synsets(self):
        """Exibe synsets e todas as relações"""
        self.text_synsets.delete("1.0", "end")
        
        text = f"Termo: {self.term_var.get()} | POS: {self.pos_var.get()} | "
        text += f"Idioma: {self.lang_var.get()} | Synsets: {len(self.current_synsets)}\n"
        text += "="*100 + "\n\n"
        
        for i, synset in enumerate(self.current_synsets, 1):
            text += f"[{i}] {synset.name()} (POS: {synset.pos()})\n"
            text += f"  📖 Definição: {synset.definition()}\n"
            
            # Exemplos
            if synset.examples():
                text += f"  💬 Exemplos: {'; '.join(synset.examples())}\n"
            
            # Lemmas e suas relações
            text += f"  📝 Lemmas: {', '.join([l.name() for l in synset.lemmas()])}\n"
            
            # Lemmas em outros idiomas (com tratamento de erros)
            other_langs = []
            for lang_name, lang_code_item in LANGUAGES.items():
                if lang_code_item != 'eng':
                    lemmas_lang = synset.lemma_names(lang=lang_code_item)
                    if lemmas_lang:
                        other_langs.append(f"    • {lang_name}: {', '.join(lemmas_lang)}")
                    elif lang_name.endswith(" *"):
                        other_langs.append(f"    • {lang_name.rstrip(' *')}: (léxico ainda não descarregado)")
            
            if other_langs:
                text += "  📌 Traduções:\n"
                for lang_text in other_langs:
                    text += lang_text + "\n"
            
            # Antônimos (via lemmas)
            antonyms = []
            for lemma in synset.lemmas():
                antonyms.extend([a.name() for a in lemma.antonyms()])
            if antonyms:
                text += f"  ↔️ Antônimos: {', '.join(set(antonyms))}\n"
            
            # Relações semânticas
            relations = [
                ("⬆️ Hiperônimos", synset.hypernyms()),
                ("⬇️ Hipônimos", synset.hyponyms()),
                ("🔹 Instância de", synset.instance_hypernyms()),
                ("🔸 Instâncias", synset.instance_hyponyms()),
                ("🔄 Similares", synset.similar_tos()),
                ("➡️ Implica", synset.entailments()),
                ("⚡ Causa", synset.causes()),
                ("👁️ Também vê", synset.also_sees()),
                ("🔗 Grupo verbal", synset.verb_groups()),
                ("📦 Holônimos (membro)", synset.member_holonyms()),
                ("📦 Holônimos (parte)", synset.part_holonyms()),
                ("📦 Holônimos (substância)", synset.substance_holonyms()),
                ("🧩 Merônimos (membro)", synset.member_meronyms()),
                ("🧩 Merônimos (parte)", synset.part_meronyms()),
                ("🧩 Merônimos (substância)", synset.substance_meronyms()),
                ("🎯 Atributos", synset.attributes()),
            ]
            
            for rel_name, rel_synsets in relations:
                if rel_synsets:
                    text += f"  {rel_name}: {_format_list([s.name() for s in rel_synsets])}\n"
            
            # Informações adicionais
            text += f"  📊 Profundidade: min={synset.min_depth()}, max={synset.max_depth()}\n"
            
            # Domínios (se disponíveis)
            try:
                topic = synset.topic_domains()
                if topic:
                    text += f"  🏷️ Domínio temático: {', '.join([t.name() for t in topic])}\n"
            except:
                pass
                
            try:
                region = synset.region_domains()
                if region:
                    text += f"  🌍 Domínio regional: {', '.join([r.name() for r in region])}\n"
            except:
                pass
                
            try:
                usage = synset.usage_domains()
                if usage:
                    text += f"  💭 Domínio de uso: {', '.join([u.name() for u in usage])}\n"
            except:
                pass
            
            # Relações lexicais dos lemmas
            for lemma in synset.lemmas()[:3]:  # Primeiros 3 lemmas
                derivations = lemma.derivationally_related_forms()
                if derivations:
                    text += f"  📚 Derivações de '{lemma.name()}': {', '.join([d.name() for d in derivations])}\n"
                
                pertainyms = lemma.pertainyms()
                if pertainyms:
                    text += f"  🔗 Pertainyms de '{lemma.name()}': {', '.join([p.name() for p in pertainyms])}\n"
            
            text += "\n" + "-"*100 + "\n\n"
        
        self.text_synsets.insert("1.0", text)
    
    def load_synsets_for_similarity(self):
        """Carrega synsets para comparação de similaridade"""
        term1 = self.sim_term1.get().strip()
        term2 = self.sim_term2.get().strip()
        
        if term1:
            synsets1 = wn.synsets(term1)
            self.sim_synset1['values'] = [s.name() for s in synsets1]
            if synsets1:
                self.sim_synset1.set(synsets1[0].name())
        
        if term2:
            synsets2 = wn.synsets(term2)
            self.sim_synset2['values'] = [s.name() for s in synsets2]
            if synsets2:
                self.sim_synset2.set(synsets2[0].name())
    
    def calculate_similarities(self):
        """Calcula todas as métricas de similaridade"""
        try:
            s1_name = self.sim_synset1.get()
            s2_name = self.sim_synset2.get()
            
            if not s1_name or not s2_name:
                messagebox.showwarning("Aviso", "Selecione dois synsets para comparar")
                return
            
            s1 = wn.synset(s1_name)
            s2 = wn.synset(s2_name)
            
            self.text_similarity.delete("1.0", "end")
            self.text_similarity.insert("1.0", "A calcular similaridades...\n")
            self.update_idletasks()

            if self.ic is None and not wordnet_ic.is_ready():
                self._set_status("A calcular Information Content (corpus Brown); aguarde...")
                self.ic = _get_ic()
            elif self.ic is None:
                self.ic = _get_ic()
            
            results = "Comparação de Similaridade\n"
            results += f"Synset 1: {s1.name()} - {s1.definition()}\n"
            results += f"Synset 2: {s2.name()} - {s2.definition()}\n"
            results += "=" * 80 + "\n\n"
            
            path_val = s1.path_similarity(s2)
            results += f"📊 Path Similarity: {format_score(path_val)}\n"
            results += "   (Baseado no caminho mais curto entre synsets)\n\n"
            
            lch_val = s1.lch_similarity(s2)
            if lch_val is not None:
                results += f"📊 Leacock-Chodorow Similarity: {format_score(lch_val)}\n"
            else:
                results += "📊 Leacock-Chodorow Similarity: N/A (POS diferentes ou sem caminho)\n"
            results += "   (Considera profundidade da taxonomia)\n\n"
            
            wup_val = s1.wup_similarity(s2)
            results += f"📊 Wu-Palmer Similarity: {format_score(wup_val)}\n"
            results += "   (Baseado na profundidade do LCS)\n\n"
            
            if self.ic:
                res_val = s1.res_similarity(s2, self.ic)
                results += f"📊 Resnik Similarity: {format_score(res_val)}\n"
                results += "   (IC do ancestral comum mais específico)\n\n"

                jcn_val = s1.jcn_similarity(s2, self.ic)
                results += f"📊 Jiang-Conrath Similarity: {format_score(jcn_val)}\n"
                results += "   (Diferença de IC)\n\n"

                lin_val = s1.lin_similarity(s2, self.ic)
                results += f"📊 Lin Similarity: {format_score(lin_val)}\n"
                results += "   (Razão de IC)\n\n"
            else:
                results += "\n⚠️ Information Content não disponível para métricas IC\n\n"
            
            # Informações adicionais
            results += "-"*80 + "\n"
            results += "Informações Relacionais:\n\n"
            
            # Distância do caminho mais curto
            dist = s1.shortest_path_distance(s2)
            results += f"🛤️ Distância do caminho mais curto: {dist if dist is not None else 'N/A'}\n"
            
            # LCS - Lowest Common Subsumer
            try:
                lcs_list = s1.lowest_common_hypernyms(s2)
                if lcs_list:
                    results += f"🎯 Hiperônimo comum mais baixo (LCS):\n"
                    for lcs in lcs_list:
                        results += f"   • {lcs.name()}: {lcs.definition()}\n"
            except:
                results += "🎯 Hiperônimo comum mais baixo: N/A\n"
            
            # Caminhos comuns
            try:
                s1_hyper = set(s1.common_hypernyms(s2))
                if s1_hyper:
                    results += f"\n🔀 Hiperônimos comuns ({len(s1_hyper)}):\n"
                    for h in list(s1_hyper)[:10]:
                        results += f"   • {h.name()}\n"
            except:
                pass
            
            self.text_similarity.delete("1.0", "end")
            self.text_similarity.insert("1.0", results)
            self._set_status("Similaridades calculadas.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular similaridade: {e}")
            self._set_status("Erro ao calcular similaridades.")
    
    def explore_hierarchy(self):
        """Explora hierarquia de um synset"""
        try:
            synset_name = self.hier_synset_var.get()
            if not synset_name:
                messagebox.showwarning("Aviso", "Selecione um synset")
                return
            
            synset = wn.synset(synset_name)
            depth = self.depth_var.get()
            
            results = f"Exploração Hierárquica: {synset.name()}\n"
            results += f"Definição: {synset.definition()}\n"
            results += "="*80 + "\n\n"
            
            # Caminhos até a raiz
            results += "🌳 CAMINHOS ATÉ A RAIZ:\n"
            paths = synset.hypernym_paths()
            for i, path in enumerate(paths[:5], 1):
                results += f"\nCaminho {i}:\n"
                for j, s in enumerate(path):
                    results += f"  {'  ' * j}→ {s.name()}: {s.definition()[:50]}...\n"
            
            # Hiperônimos raiz
            results += "\n🎯 HIPERÔNIMOS RAIZ:\n"
            for root in synset.root_hypernyms():
                results += f"  • {root.name()}: {root.definition()}\n"
            
            # Closure (fechamento transitivo)
            results += f"\n📊 FECHAMENTO TRANSITIVO (profundidade {depth}):\n"
            
            # Hiperônimos
            hyper_closure = list(synset.closure(lambda s: s.hypernyms(), depth=depth))
            results += f"\n⬆️ Hiperônimos ({len(hyper_closure)}):\n"
            for h in hyper_closure[:20]:
                results += f"  • {h.name()}\n"
            
            # Hipônimos
            hypo_closure = list(synset.closure(lambda s: s.hyponyms(), depth=depth))
            results += f"\n⬇️ Hipônimos ({len(hypo_closure)}):\n"
            for h in hypo_closure[:20]:
                results += f"  • {h.name()}\n"
            
            # Informações de profundidade
            results += f"\n📏 MÉTRICAS DE PROFUNDIDADE:\n"
            results += f"  • Profundidade mínima: {synset.min_depth()}\n"
            results += f"  • Profundidade máxima: {synset.max_depth()}\n"
            
            # Árvore
            results += f"\n🌲 ÁRVORE DE HIPERÔNIMOS (simplificada):\n"
            tree = synset.tree(lambda s: s.hypernyms(), depth=3)
            results += self._format_tree(tree, 0)
            
            self.text_hierarchy.delete("1.0", "end")
            self.text_hierarchy.insert("1.0", results)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao explorar hierarquia: {e}")
    
    def _format_tree(self, tree, indent=0):
        """Formata árvore para exibição"""
        result = ""
        if isinstance(tree, list):
            for item in tree:
                result += self._format_tree(item, indent)
        else:
            result += "  " * indent + f"• {tree.name()}\n"
            if hasattr(tree, '__iter__'):
                for child in tree:
                    if isinstance(child, list):
                        result += self._format_tree(child, indent + 1)
        return result
    
    def analyze_morphy(self):
        """Análise morfológica com morphy"""
        word = self.morphy_input.get().strip()
        if not word:
            return
        
        results = f"Análise Morfológica: '{word}'\n"
        results += "="*60 + "\n\n"
        
        # Morphy para cada POS
        for pos_name, pos_tag in [("Substantivo", wn.NOUN), ("Verbo", wn.VERB), 
                                  ("Adjetivo", wn.ADJ), ("Advérbio", wn.ADV)]:
            lemma = wn.morphy(word, pos=pos_tag)
            if lemma:
                results += f"📝 {pos_name}: {lemma}\n"
                
                # Synsets correspondentes
                synsets = wn.synsets(lemma, pos=pos_tag)
                if synsets:
                    results += f"   Synsets: {', '.join([s.name() for s in synsets[:5]])}\n"
        
        # Lematização com WordNetLemmatizer (se disponível)
        if self.lemmatizer:
            results += f"\n🔧 WordNetLemmatizer:\n"
            for pos_name, pos_tag in [("n", "n"), ("v", "v"), ("a", "a"), ("r", "r")]:
                try:
                    lemma = self.lemmatizer.lemmatize(word, pos=pos_tag)
                    results += f"   POS '{pos_tag}': {lemma}\n"
                except:
                    results += f"   POS '{pos_tag}': [erro]\n"
        else:
            results += "\n⚠ WordNetLemmatizer não disponível\n"
        
        # Todas as formas possíveis
        results += f"\n📚 Todas as formas base possíveis:\n"
        all_morphs = set()
        for pos in [wn.NOUN, wn.VERB, wn.ADJ, wn.ADV]:
            m = wn.morphy(word, pos=pos)
            if m:
                all_morphs.add(m)
        
        if all_morphs:
            for morph in all_morphs:
                results += f"   • {morph}\n"
                # Definições
                synsets = wn.synsets(morph)
                if synsets:
                    results += f"     Definições:\n"
                    for s in synsets[:3]:
                        results += f"       - {s.name()}: {s.definition()[:60]}...\n"
        else:
            results += "   Nenhuma forma base encontrada\n"
        
        self.text_morphy.delete("1.0", "end")
        self.text_morphy.insert("1.0", results)
    
    def analyze_domains(self):
        """Analisa domínios semânticos"""
        if not self.current_synsets:
            self.text_domains.insert("1.0", "Faça uma busca primeiro para carregar synsets")
            return
        
        results = "Análise de Domínios Semânticos\n"
        results += "="*60 + "\n\n"
        
        topic_domains = defaultdict(list)
        region_domains = defaultdict(list)
        usage_domains = defaultdict(list)
        
        for synset in self.current_synsets:
            # Topic domains
            try:
                topics = synset.topic_domains()
                for t in topics:
                    topic_domains[t.name()].append(synset.name())
            except:
                pass
            
            # Region domains
            try:
                regions = synset.region_domains()
                for r in regions:
                    region_domains[r.name()].append(synset.name())
            except:
                pass
            
            # Usage domains
            try:
                usages = synset.usage_domains()
                for u in usages:
                    usage_domains[u.name()].append(synset.name())
            except:
                pass
        
        # Exibir resultados
        if topic_domains:
            results += "🏷️ DOMÍNIOS TEMÁTICOS:\n"
            for domain, synsets in topic_domains.items():
                results += f"  {domain}:\n"
                for s in synsets:
                    results += f"    • {s}\n"
            results += "\n"
        
        if region_domains:
            results += "🌍 DOMÍNIOS REGIONAIS:\n"
            for domain, synsets in region_domains.items():
                results += f"  {domain}:\n"
                for s in synsets:
                    results += f"    • {s}\n"
            results += "\n"
        
        if usage_domains:
            results += "💭 DOMÍNIOS DE USO:\n"
            for domain, synsets in usage_domains.items():
                results += f"  {domain}:\n"
                for s in synsets:
                    results += f"    • {s}\n"
        
        if not (topic_domains or region_domains or usage_domains):
            results += "Nenhum domínio semântico encontrado para os synsets atuais.\n"
            results += "(Nota: nem todos os synsets têm domínios definidos)\n"
        
        self.text_domains.delete("1.0", "end")
        self.text_domains.insert("1.0", results)
    
    def get_verb_frames(self):
        """Obtém frames de sentença para verbos"""
        verb = self.verb_input.get().strip()
        if not verb:
            return
        
        results = f"Frames de Sentença para: '{verb}'\n"
        results += "="*60 + "\n\n"
        
        synsets = wn.synsets(verb, pos=wn.VERB)
        
        if not synsets:
            results += f"Nenhum synset verbal encontrado para '{verb}'\n"
        else:
            for synset in synsets:
                results += f"📌 {synset.name()}: {synset.definition()}\n"
                
                for lemma in synset.lemmas():
                    frames = lemma.frame_strings()
                    if frames:
                        results += f"  Lemma: {lemma.name()}\n"
                        for frame in frames:
                            # Substituir placeholders
                            frame_formatted = frame.replace("%s", f"[{lemma.name().upper()}]")
                            results += f"    • {frame_formatted}\n"
                
                results += "\n"
        
        self.text_frames.delete("1.0", "end")
        self.text_frames.insert("1.0", results)
    
    def calculate_ic(self):
        """Calcula Information Content dos synsets"""
        if not self.current_synsets:
            self.text_ic.insert("1.0", "Faça uma busca primeiro para carregar synsets")
            return
        
        if not self.ic:
            if not wordnet_ic.is_ready():
                self._set_status("A calcular Information Content...")
                self.ic = _get_ic()
            else:
                self.ic = _get_ic()
        if not self.ic:
            self.text_ic.insert("1.0", "Information Content corpus não disponível")
            return
        
        results = "Information Content Analysis\n"
        results += f"Corpus: {self.ic_corpus_var.get()}\n"
        results += "="*60 + "\n\n"
        
        ic_values = []
        
        for synset in self.current_synsets:
            try:
                ic_value = information_content_value(synset, self.ic)
                ic_values.append((synset.name(), ic_value))
                
                results += f"📊 {synset.name()}\n"
                results += f"   IC: {ic_value:.4f}\n"
                results += f"   Definição: {synset.definition()[:60]}...\n\n"
            except Exception as e:
                results += f"❌ {synset.name()}: Erro ao calcular IC\n\n"
        
        # Estatísticas
        if ic_values:
            ic_nums = [v for _, v in ic_values]
            results += "-"*60 + "\n"
            results += "ESTATÍSTICAS:\n"
            results += f"  • IC Médio: {sum(ic_nums)/len(ic_nums):.4f}\n"
            results += f"  • IC Mínimo: {min(ic_nums):.4f}\n"
            results += f"  • IC Máximo: {max(ic_nums):.4f}\n"
            
            # Ordenar por IC
            results += "\nRANKING POR IC (maior → menor especificidade):\n"
            for name, ic_val in sorted(ic_values, key=lambda x: x[1], reverse=True):
                results += f"  {ic_val:.4f} - {name}\n"
        
        self.text_ic.delete("1.0", "end")
        self.text_ic.insert("1.0", results)
    
    # Mapeia cada tipo de relação -> (rótulo, cor, estilo de linha, método do synset)
    _GRAPH_RELATIONS = {
        "hypernym": ("Hiperônimo", "#1f77b4", "solid", "hypernyms"),
        "hyponym": ("Hipônimo", "#2ca02c", "solid", "hyponyms"),
        "similar": ("Similar", "#9467bd", "dashed", "similar_tos"),
        "part_meronym": ("Merônimo (parte)", "#ff7f0e", "solid", "part_meronyms"),
        "member_holonym": ("Holônimo (membro)", "#8c564b", "solid", "member_holonyms"),
        "cause": ("Causa", "#d62728", "solid", "causes"),
        "entailment": ("Implica", "#e377c2", "solid", "entailments"),
    }

    def _graph_relation_keys(self, graph_type: str) -> list:
        """Relações a desenhar consoante o tipo de grafo escolhido."""
        if graph_type == "Hiperônimos":
            return ["hypernym"]
        if graph_type == "Hipônimos":
            return ["hyponym"]
        if graph_type == "Similares":
            return ["similar"]
        return ["hypernym", "hyponym", "similar",
                "part_meronym", "member_holonym", "cause", "entailment"]

    @staticmethod
    def _synset_label(synset) -> str:
        """Rótulo legível (palavras do synset) em vez do ID interno."""
        try:
            names = [l.name() for l in synset.lemmas()]
        except Exception:
            names = []
        if not names:
            return synset.name()
        label = ", ".join(names[:3])
        if len(names) > 3:
            label += "…"
        return label

    def _collect_graph_data(self, graph_type, max_neighbors):
        """Colher nós e arestas do grafo (dados puros, sem desenhar).

        Devolve (nodes, edges, rel_keys) onde nodes é {id: {label, ili, central}}
        e edges é uma lista de (origem, destino, chave_de_relação). Partilhado
        pelo desenho no ecrã e pela exportação.
        """
        rel_keys = self._graph_relation_keys(graph_type)
        max_neighbors = max(1, int(max_neighbors))
        nodes: Dict[str, dict] = {}
        edges: List[tuple] = []

        def _register(synset, central=False):
            node_id = synset.name()
            if node_id not in nodes:
                try:
                    ili = synset.ili()
                except Exception:
                    ili = None
                nodes[node_id] = {"label": self._synset_label(synset),
                                  "ili": ili, "central": central}
            if central:
                nodes[node_id]["central"] = True
            return node_id

        for synset in self.current_synsets[:6]:
            src = _register(synset, central=True)
            for key in rel_keys:
                getter = self._GRAPH_RELATIONS[key][3]
                try:
                    related = getattr(synset, getter)()[:max_neighbors]
                except Exception:
                    related = []
                for target in related:
                    dst = _register(target)
                    if dst != src:
                        edges.append((src, dst, key))
        return nodes, edges, rel_keys

    def _build_graph_figure(self, graph_type, max_neighbors):
        """Construir (sem embutir) a figura matplotlib do grafo. None se vazio."""
        nodes, edges, rel_keys = self._collect_graph_data(graph_type, max_neighbors)
        if not nodes:
            return None

        G = nx.DiGraph()
        labels = {}
        central_ids = set()
        for nid, meta in nodes.items():
            G.add_node(nid)
            labels[nid] = meta["label"]
            if meta.get("central"):
                central_ids.add(nid)
        for src, dst, key in edges:
            G.add_edge(src, dst, rel=key)

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111)

        seed_nodes = max(G.number_of_nodes(), 1)
        pos = nx.spring_layout(G, k=2.2 / (seed_nodes ** 0.5), iterations=80, seed=42)

        central = [n for n in G if n in central_ids]
        neighbors = [n for n in G if n not in central_ids]
        nx.draw_networkx_nodes(G, pos, nodelist=neighbors, ax=ax,
                               node_color="#add1e6", node_size=1700,
                               edgecolors="#5a8fb5", linewidths=1.0)
        nx.draw_networkx_nodes(G, pos, nodelist=central, ax=ax,
                               node_color="#f4a582", node_size=2400,
                               edgecolors="#c1663a", linewidths=1.4)

        used_keys = []
        for key in rel_keys:
            _label, color, style, _getter = self._GRAPH_RELATIONS[key]
            ekeys = [(u, v) for u, v, d in G.edges(data=True) if d.get("rel") == key]
            if not ekeys:
                continue
            used_keys.append(key)
            nx.draw_networkx_edges(
                G, pos, edgelist=ekeys, ax=ax, edge_color=color, width=1.6,
                style=style, arrows=True, arrowsize=16, arrowstyle="-|>",
                connectionstyle="arc3,rad=0.06",
            )

        nx.draw_networkx_labels(G, pos, labels=labels, ax=ax,
                                font_size=8, font_weight="bold")

        handles = [
            Patch(facecolor="#f4a582", edgecolor="#c1663a", label="Synset pesquisado"),
            Patch(facecolor="#add1e6", edgecolor="#5a8fb5", label="Synset relacionado"),
        ]
        for key in used_keys:
            label, color, style, _getter = self._GRAPH_RELATIONS[key]
            handles.append(Line2D([0], [0], color=color, lw=2,
                                  linestyle="--" if style == "dashed" else "-",
                                  label=label))
        ax.legend(handles=handles, loc="upper left", fontsize=8,
                  framealpha=0.9, borderaxespad=0.3)

        ax.set_title(f"Grafo de {graph_type} — «{self.term_var.get()}»", fontsize=12)
        ax.set_axis_off()
        fig.tight_layout()
        return fig

    def generate_graph(self):
        """Gera visualização em grafo com rótulos legíveis e relações coloridas."""
        if not HAS_GRAPH:
            messagebox.showinfo("Aviso", "matplotlib/networkx não estão instalados.")
            return
        if not self.current_synsets:
            messagebox.showinfo("Aviso", "Pesquise um termo primeiro para carregar synsets.")
            return

        try:
            # Fechar figura anterior (evita fuga de memória do matplotlib).
            if self._graph_fig is not None:
                plt.close(self._graph_fig)
                self._graph_fig = None
            for widget in self.graph_frame.winfo_children():
                widget.destroy()

            graph_type = self.graph_type.get()
            max_neighbors = max(1, int(self.graph_neighbors.get()))
            self._graph_fig = self._build_graph_figure(graph_type, max_neighbors)
            if self._graph_fig is None:
                messagebox.showinfo("Aviso", "Nenhum nó para desenhar.")
                return

            self._graph_canvas = FigureCanvasTkAgg(self._graph_fig, self.graph_frame)
            self._graph_canvas.draw()
            toolbar = NavigationToolbar2Tk(self._graph_canvas, self.graph_frame)
            toolbar.update()
            self._graph_canvas.get_tk_widget().pack(fill="both", expand=True)

            nodes, edges, _ = self._collect_graph_data(graph_type, max_neighbors)
            self._set_status(
                f"Grafo gerado: {len(nodes)} nós, {len(edges)} relações ({graph_type})."
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao gerar grafo: {e}")
    
    def _open_exports_folder(self):
        path = ensure_exports_dir()
        try:
            os.startfile(path)  # type: ignore[attr-defined]
        except Exception:
            messagebox.showinfo("exports", str(path))

    def export_all(self):
        """Exporta TODAS as vertentes (synsets & relações, similaridade,
        hierarquia e visualização). Pasta inicial: WordNet/exports/."""
        if not self.current_synsets:
            messagebox.showinfo("Aviso", "Nenhum dado para exportar")
            return

        ensure_exports_dir()
        # Fase 0 / LexWarrant result is available; full facets JSON is better
        # for “everything”. Dialog still offers both.
        filetypes = [
            ("JSON completo (todas as facetas)", "*.json"),
            ("Relatório Markdown", "*.md"),
            ("Fase 0 / LexWarrant (result.json)", "*.result.json"),
            ("Texto", "*.txt"),
            ("CSV (tabelas)", "*.csv"),
        ]
        if HAS_GRAPH:
            filetypes.append(("Imagem do grafo (PNG)", "*.png"))
        slug = _safe_export_slug(self.term_var.get())
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=filetypes,
            initialdir=str(EXPORTS_DIR),
            initialfile=f"{slug}.facets.json",
        )
        if not filename:
            return

        try:
            ext = os.path.splitext(filename)[1].lower()
            extra = None
            if filename.lower().endswith(".result.json"):
                if not self._export_fase0_result(filename):
                    return  # user cancelled the class prompt
            elif ext == ".json":
                self._export_json(filename)
            elif ext == ".csv":
                extra = self._export_csv(filename)
            elif ext == ".png":
                self._export_graph_png(filename)
            elif ext == ".txt":
                self._export_report(filename, markdown=False)
                extra = self._maybe_export_graph_sidecar(filename)
            else:
                self._export_report(filename, markdown=True)
                extra = self._maybe_export_graph_sidecar(filename)

            note = f"Dados exportados para:\n{filename}"
            if extra:
                note += "\n\nFicheiros adicionais:\n• " + "\n• ".join(extra)
            self._set_status(f"Exportado: {os.path.basename(filename)}")
            messagebox.showinfo("Sucesso", note)

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao exportar: {e}")

    def export_all_to_exports(self):
        """One-click: dump synsets/relations + similarity + hierarchy + graph
        into WordNet/exports/<termo>_<timestamp>/."""
        if not self.current_synsets:
            messagebox.showinfo("Aviso", "Nenhum dado para exportar — pesquise primeiro.")
            return
        import datetime

        ensure_exports_dir()
        slug = _safe_export_slug(self.term_var.get())
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bundle = EXPORTS_DIR / f"{slug}_{stamp}"
        bundle.mkdir(parents=True, exist_ok=True)
        base = bundle / slug
        written: list[str] = []

        try:
            # 1) Full structured facets (synsets, relations, similarity,
            #    hierarchy, visualization)
            facets_path = f"{base}.facets.json"
            self._export_json(facets_path)
            written.append(facets_path)

            # 2) Human report + graph sidecar
            md_path = f"{base}.report.md"
            self._export_report(md_path, markdown=True)
            written.append(md_path)
            for extra in self._maybe_export_graph_sidecar(md_path) or []:
                written.append(extra)

            # 3) CSV tables
            csv_path = f"{base}.synsets.csv"
            extras = self._export_csv(csv_path) or []
            written.append(csv_path)
            for extra in extras:
                if extra not in written:
                    written.append(extra)

            # 4) Standalone graph PNG (if available)
            if HAS_GRAPH:
                png_path = f"{base}.graph.png"
                try:
                    self._export_graph_png(png_path)
                    if png_path not in written:
                        written.append(png_path)
                except Exception:
                    pass

            note = (
                "Exportação completa (synsets & relações, similaridade, "
                "hierarquia, visualização)\n\n"
                f"Pasta:\n{bundle}\n\nFicheiros:\n• "
                + "\n• ".join(os.path.basename(p) for p in written)
            )
            self._set_status(f"Exportado → exports/{bundle.name}")
            messagebox.showinfo("Sucesso — exports/", note)
            try:
                os.startfile(bundle)  # type: ignore[attr-defined]
            except Exception:
                pass
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao exportar para exports/: {e}")
    
    # --- Alignment policy (Fase 0 bi-source engine) ----------------------
    # ILI is the PRIMARY cross-resource key; the PT alignment is obtained via
    # translate() (ILI-mediated), NOT by string-matching offsets. ILI is never
    # derived from the oewn id by string manipulation. Synsets whose ili is None
    # are exported with ili=null (not dropped, not force-matched) so the
    # downstream engine can route them to sinalização.
    def _rel_targets(self, synsets):
        """Uniform synset-level relation targets; drops lemma-less targets."""
        out = []
        for s in synsets:
            gloss = s.definition() or ""
            words = [l.name() for l in s.lemmas()]
            if not words:            # skip lemma-less targets
                continue
            out.append({"id": s.name(), "ili": s.ili(), "words": words, "gloss": gloss})
        return out

    def _lemma_rel_targets(self, synset, method):
        """Aggregate lemma-level relations (antonym/derivation) up to synset level."""
        seen, out = set(), []
        for lemma in synset.lemmas():
            for rel_lemma in getattr(lemma, method)():
                tgt = rel_lemma.synset()
                key = tgt.name()
                if key in seen:
                    continue
                seen.add(key)
                words = [l.name() for l in tgt.lemmas()]
                if not words:
                    continue
                out.append({"id": key, "ili": tgt.ili(), "words": words,
                            "gloss": tgt.definition() or ""})
        return out

    # --- Facet collectors (shared by every writer) -----------------------
    def _facet_synset(self, synset) -> dict:
        """Synset & relations facet — keeps the Fase 0 bi-source schema intact."""
        return {
            "name": synset.name(),
            "ili": synset.ili(),                       # canonical cross-resource key
            "pos": synset.pos(),
            "definition": synset.definition(),
            "examples": synset.examples(),
            "lemmas": [l.name() for l in synset.lemmas()],
            "pt_lemmas": synset.pt_lemmas(),           # ILI-mediated PT alignment
            "hypernyms": [h.name() for h in synset.hypernyms()],
            "hyponyms": [h.name() for h in synset.hyponyms()],
            "min_depth": synset.min_depth(),
            "max_depth": synset.max_depth(),
            "relations": {                             # typed relations
                "antonym": self._lemma_rel_targets(synset, "antonyms"),
                "derivationally_related_form":
                    self._lemma_rel_targets(synset, "derivationally_related_forms"),
                "similar_to": self._rel_targets(synset.similar_tos()),
                "attribute":  self._rel_targets(synset.attributes()),
                "also_see":   self._rel_targets(synset.also_sees()),
            },
        }

    def _facet_similarity(self, limit=12) -> dict:
        """Pairwise similarity across the current synsets (IC metrics if loaded)."""
        import itertools
        ic = getattr(self, "ic", None)
        chosen = self.current_synsets[:limit]
        pairs = []
        for a, b in itertools.combinations(chosen, 2):
            def _try(fn, *args):
                try:
                    return fn(*args)
                except Exception:
                    return None
            # NOTE: lch_similarity is intentionally NOT computed in bulk — it
            # rescans the whole taxonomy for max-depth (~tens of seconds/call).
            # The interactive «Similaridade» tab still reports it per single pair.
            rec = {
                "a": a.name(), "b": b.name(),
                "path": _try(a.path_similarity, b),
                "wup": _try(a.wup_similarity, b),
                "shortest_path_distance": _try(a.shortest_path_distance, b),
            }
            if ic:
                rec["res"] = _try(a.res_similarity, b, ic)
                rec["jcn"] = _try(a.jcn_similarity, b, ic)
                rec["lin"] = _try(a.lin_similarity, b, ic)
            lcs = _try(a.lowest_common_hypernyms, b) or []
            rec["lowest_common_hypernyms"] = [s.name() for s in lcs]
            pairs.append(rec)
        notes = ["lch (Leacock-Chodorow) omitido no relatório em massa por custo "
                 "(recalcula a profundidade da taxonomia); use a aba Similaridade."]
        if not ic:
            notes.append("IC ainda não carregado; métricas Resnik/JCN/Lin omitidas.")
        return {
            "ic_loaded": bool(ic),
            "ic_corpus": getattr(self, "ic_corpus_var", None) and self.ic_corpus_var.get(),
            "note": " ".join(notes),
            "n_synsets": len(chosen),
            "truncated": len(self.current_synsets) > limit,
            "pairs": pairs,
        }

    def _facet_hierarchy(self, depth=None) -> dict:
        """Hypernym paths, roots, closures and depths per current synset."""
        if depth is None:
            depth = getattr(self, "depth_var", None) and self.depth_var.get() or 3
        out = {}
        for s in self.current_synsets:
            def _names(fn, cap=None):
                try:
                    items = list(fn())
                except Exception:
                    return []
                return [x.name() for x in (items[:cap] if cap else items)]
            try:
                paths = [[n.name() for n in p] for p in s.hypernym_paths()[:5]]
            except Exception:
                paths = []
            out[s.name()] = {
                "min_depth": s.min_depth(),
                "max_depth": s.max_depth(),
                "root_hypernyms": _names(s.root_hypernyms),
                "hypernym_paths": paths,
                "hypernym_closure": _names(
                    lambda: s.closure(lambda x: x.hypernyms(), depth=depth), cap=40),
                "hyponym_closure": _names(
                    lambda: s.closure(lambda x: x.hyponyms(), depth=depth), cap=40),
            }
        return {"depth": depth, "synsets": out}

    def _facet_visualization(self) -> dict:
        """Graph nodes/edges (the same data the Visualização tab draws)."""
        if not HAS_GRAPH:
            return {"available": False,
                    "note": "matplotlib/networkx não instalados"}
        graph_type = getattr(self, "graph_type", None) and self.graph_type.get() or "Todos"
        max_neighbors = (getattr(self, "graph_neighbors", None)
                         and self.graph_neighbors.get()) or 4
        nodes, edges, rel_keys = self._collect_graph_data(graph_type, max_neighbors)
        legend = {k: {"label": v[0], "color": v[1], "style": v[2]}
                  for k, v in self._GRAPH_RELATIONS.items() if k in rel_keys}
        return {
            "available": True,
            "graph_type": graph_type,
            "max_neighbors": max_neighbors,
            "relation_legend": legend,
            "nodes": [{"id": nid, **meta} for nid, meta in nodes.items()],
            "edges": [{"source": s, "target": t, "rel": k,
                       "rel_label": self._GRAPH_RELATIONS[k][0]} for s, t, k in edges],
        }

    def _collect_all_facets(self) -> dict:
        """Assemble every facet into one structured dict (used by all writers)."""
        import datetime
        data = {
            "term": self.term_var.get(),
            "pos": self.pos_var.get(),
            "language": self.lang_var.get(),
            "generated": datetime.datetime.now().isoformat(timespec="seconds"),
            "facets": ["synsets_relations", "similarity", "hierarchy", "visualization"],
            # Provenance: ILI-mediated alignment (never offset string-matching).
            "source": {"lexicon": "oewn", "backend": "wn",
                       "alignment": "ILI via translate()"},
            "synsets": [self._facet_synset(s) for s in self.current_synsets],
            "similarity": self._facet_similarity(),
            "hierarchy": self._facet_hierarchy(),
            "visualization": self._facet_visualization(),
        }
        # Report the PT-alignment state ACCURATELY: distinguish «own-pt not
        # installed» from «installed but this batch of synsets has no PT synset».
        n_pt = sum(1 for s in data["synsets"] if s["pt_lemmas"])
        n_all = len(data["synsets"])
        try:
            pt_installed = wn.own_pt_installed()
        except Exception:  # noqa: BLE001
            pt_installed = False
        if not pt_installed:
            data["source"]["note"] = ("own-pt (OpenWordNet-PT) não instalado; "
                                       "pt_lemmas vazios")
        elif n_pt == 0:
            data["source"]["note"] = ("own-pt instalado, mas nenhum synset em ecrã "
                                      "tem correspondência PT (pt_lemmas vazios)")
        else:
            data["source"]["pt_coverage"] = f"{n_pt}/{n_all} synsets com pt_lemmas"
        return data

    # --- Writers ---------------------------------------------------------
    def _export_json(self, filename):
        """Exporta TODAS as vertentes em JSON estruturado (facetas — leitura)."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self._collect_all_facets(), f, indent=2, ensure_ascii=False)

    def _export_fase0_result(self, filename) -> bool:
        """Escreve um «<classe>.result.json» compatível com a LexWarrant.

        A WordNet é a referência interlingual: NÃO admite termos (UF/RT) porque não
        passa pelo protocolo de adjudicação humana do ONTO/PULO. Entra como
        CORROBORAÇÃO — cada lema (PT via ILI, ou inglês se não houver alinhamento)
        dos synsets em ecrã é registado em `sinalizacao`, ancorado no ILI. Devolve
        False se o utilizador cancelar (para não gravar um ficheiro vazio de classe).
        """
        import datetime
        import unicodedata

        def _norm(w: str) -> str:
            nf = unicodedata.normalize("NFKD", w or "")
            return "".join(c for c in nf if not unicodedata.combining(c)).lower().replace(" ", "_")

        term = (self.term_var.get() or "Classe").strip()
        default_cls = "".join(ch for ch in term.title() if ch.isalnum()) or "Classe"
        cls = simpledialog.askstring(
            "Fase 0 / LexWarrant",
            "Nome da CLASSE (tem de ser IGUAL ao usado no ONTO e no PULO,\n"
            "por exemplo: TexturaUniforme):",
            initialvalue=default_cls)
        if not cls:
            return False
        cls = cls.strip()

        # Self-check on the way out: prove the ILI→own-pt bridge is live (logs the
        # PT lemmas for oewn-01973553-a), so a stale/empty export is obvious.
        try:
            wn.pt_alignment_selfcheck()
        except Exception:  # noqa: BLE001
            pass

        facets = self._collect_all_facets()
        sina: dict = {}
        for syn in facets.get("synsets", []):
            ili = syn.get("ili")
            words = syn.get("pt_lemmas") or []
            via = "pt_lemma (ILI)"
            if not words:
                words = syn.get("lemmas") or []
                # own-pt IS installed; this SPECIFIC synset simply has no PT synset.
                via = "en_lemma (este synset sem correspondência em own-pt)"
            for w in words:
                nw = _norm(w)
                if not nw or nw in sina:
                    continue
                sina[nw] = {
                    "display": (w or "").replace("_", " "),
                    "reason": f"atestado na WordNet [{via}] · {syn.get('name')} · ILI {ili or '—'}",
                    "offsets_ili": [ili] if ili else [],
                }

        # Per-synset block (NON-LOSSY): sinalizacao dedupes lemmas by word across
        # synsets, which drops the same lemma from a second synset (e.g. «uniforme»
        # shared by an adjective AND a noun synset). The equivalence builder needs
        # each synset's OWN pt_lemmas+POS, so carry them verbatim here (LexWarrant
        # ignores this key). build_ili_equivalence prefers `synsets` over sinalizacao.
        syn_block = [{"name": s.get("name"), "ili": s.get("ili"), "pos": s.get("pos"),
                      "pt_lemmas": list(s.get("pt_lemmas") or []),
                      "lemmas": list(s.get("lemmas") or [])}
                     for s in facets.get("synsets", [])]
        result = {
            "class_id": cls,
            "pref_label": cls,
            "axis": "(referência WordNet — corroboração por termo/ILI; sem adjudicação humana)",
            "generated": datetime.datetime.now().isoformat(timespec="seconds"),
            "source": "WordNet (OEWN via wn)",
            "oewn_version": getattr(wn, "OEWN_LEXICON", None),
            "own_pt_installed": (wn.own_pt_installed() if hasattr(wn, "own_pt_installed") else None),
            "query": {"term": term, "pos": self.pos_var.get(), "language": self.lang_var.get()},
            "provenance": [],          # WordNet não admite (sem protocolo UF/RT)
            "synsets": syn_block,      # evidência por-synset (para a tabela ILI)
            "sinalizacao": sina,       # corroboração ancorada no ILI
            "_note": ("A WordNet entra na LexWarrant como CORROBORAÇÃO (sinalização). "
                      "Não propõe estatutos UF/RT porque não passou pela adjudicação "
                      "humana; serve para confirmar termos que o ONTO/PULO admitem."),
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        return True

    def _export_csv(self, filename) -> list:
        """Exporta tabelas CSV: synsets (ficheiro base) + similaridade (irmão)."""
        base, _ = os.path.splitext(filename)
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['synset', 'ili', 'pos', 'definition', 'examples', 'lemmas',
                          'pt_lemmas', 'hypernyms', 'hyponyms', 'min_depth', 'max_depth']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for synset in self.current_synsets:
                writer.writerow({
                    'synset': synset.name(),
                    'ili': synset.ili() or '',
                    'pos': synset.pos(),
                    'definition': synset.definition(),
                    'examples': '|'.join(synset.examples()),
                    'lemmas': '|'.join([l.name() for l in synset.lemmas()]),
                    'pt_lemmas': '|'.join(synset.pt_lemmas() or []),
                    'hypernyms': '|'.join([h.name() for h in synset.hypernyms()]),
                    'hyponyms': '|'.join([h.name() for h in synset.hyponyms()]),
                    'min_depth': synset.min_depth(),
                    'max_depth': synset.max_depth(),
                })
        extra = []
        sim = self._facet_similarity()
        if sim["pairs"]:
            sim_path = base + ".similarity.csv"
            cols = ['a', 'b', 'path', 'lch', 'wup', 'res', 'jcn', 'lin',
                    'shortest_path_distance', 'lowest_common_hypernyms']
            with open(sim_path, 'w', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
                w.writeheader()
                for p in sim["pairs"]:
                    row = dict(p)
                    row['lowest_common_hypernyms'] = '|'.join(
                        p.get('lowest_common_hypernyms', []))
                    w.writerow(row)
            extra.append(sim_path)
        extra += (self._maybe_export_graph_sidecar(filename) or [])
        return extra

    def _fmt(self, v) -> str:
        return format_score(v) if isinstance(v, float) else ("—" if v is None else str(v))

    def _export_report(self, filename, markdown=True):
        """Relatório humano com TODAS as vertentes (Markdown ou texto simples)."""
        d = self._collect_all_facets()
        H1, H2, BUL = ("# ", "## ", "- ") if markdown else ("", "", "  • ")
        L = []
        ap = L.append
        ap(f"{H1}WordNet — «{d['term']}»  (POS: {d['pos']}, idioma: {d['language']})")
        ap(f"_Gerado: {d['generated']} · alinhamento: {d['source']['alignment']}_"
           if markdown else f"Gerado: {d['generated']}")
        if d["source"].get("note"):
            ap(f"> {d['source']['note']}" if markdown else f"NOTA: {d['source']['note']}")
        ap("")

        # 1) Synsets & relações
        ap(f"{H2}1. Synsets & Relações ({len(d['synsets'])})")
        for i, s in enumerate(d["synsets"], 1):
            ap("")
            ap(f"{BUL}**[{i}] {s['name']}**  (POS {s['pos']}, ILI {s['ili'] or '—'})"
               if markdown else f"[{i}] {s['name']}  (POS {s['pos']}, ILI {s['ili'] or '—'})")
            ap(f"    def.: {s['definition']}")
            if s['examples']:
                ap(f"    ex.: {'; '.join(s['examples'])}")
            ap(f"    lemmas: {', '.join(s['lemmas'])}")
            if s['pt_lemmas']:
                ap(f"    PT: {', '.join(s['pt_lemmas'])}")
            if s['hypernyms']:
                ap(f"    ⬆ hiperónimos: {', '.join(s['hypernyms'])}")
            if s['hyponyms']:
                ap(f"    ⬇ hipónimos: {_format_list(s['hyponyms'])}")
            for rel_name, targets in s["relations"].items():
                if targets:
                    ap(f"    {rel_name}: "
                       + ', '.join(t['words'][0] if t['words'] else t['id'] for t in targets))

        # 2) Similaridade
        sim = d["similarity"]
        ap("")
        ap(f"{H2}2. Similaridade (pares; IC {'carregado' if sim['ic_loaded'] else 'não carregado'})")
        if sim.get("note"):
            ap(f"> {sim['note']}" if markdown else f"NOTA: {sim['note']}")
        if sim["pairs"]:
            if markdown:
                ap("")
                ap("| A | B | path | lch | wup | res | jcn | lin | dist | LCS |")
                ap("|---|---|------|-----|-----|-----|-----|-----|------|-----|")
                for p in sim["pairs"]:
                    ap("| {a} | {b} | {path} | {lch} | {wup} | {res} | {jcn} | {lin} | "
                       "{dist} | {lcs} |".format(
                           a=p['a'], b=p['b'], path=self._fmt(p.get('path')),
                           lch=self._fmt(p.get('lch')), wup=self._fmt(p.get('wup')),
                           res=self._fmt(p.get('res')), jcn=self._fmt(p.get('jcn')),
                           lin=self._fmt(p.get('lin')),
                           dist=self._fmt(p.get('shortest_path_distance')),
                           lcs=', '.join(p.get('lowest_common_hypernyms', [])) or '—'))
            else:
                for p in sim["pairs"]:
                    ap(f"{BUL}{p['a']} ↔ {p['b']}: path={self._fmt(p.get('path'))}, "
                       f"wup={self._fmt(p.get('wup'))}, lch={self._fmt(p.get('lch'))}, "
                       f"res={self._fmt(p.get('res'))}, jcn={self._fmt(p.get('jcn'))}, "
                       f"lin={self._fmt(p.get('lin'))}, dist="
                       f"{self._fmt(p.get('shortest_path_distance'))}, "
                       f"LCS={', '.join(p.get('lowest_common_hypernyms', [])) or '—'}")
        else:
            ap("(São precisos ≥2 synsets para comparar.)")

        # 3) Hierarquia
        hier = d["hierarchy"]
        ap("")
        ap(f"{H2}3. Hierarquia (profundidade {hier['depth']})")
        for name, h in hier["synsets"].items():
            ap("")
            ap(f"{BUL}**{name}** — profundidade min={h['min_depth']}, max={h['max_depth']}"
               if markdown else f"{name} — min={h['min_depth']}, max={h['max_depth']}")
            ap(f"    raízes: {', '.join(h['root_hypernyms']) or '—'}")
            for j, path in enumerate(h["hypernym_paths"], 1):
                ap(f"    caminho {j}: {' → '.join(path)}")
            if h["hyponym_closure"]:
                ap(f"    hipónimos (fecho): {_format_list(h['hyponym_closure'])}")

        # 4) Visualização
        vis = d["visualization"]
        ap("")
        ap(f"{H2}4. Visualização (grafo)")
        if not vis.get("available"):
            ap(f"(indisponível: {vis.get('note', '')})")
        else:
            ap(f"Tipo: {vis['graph_type']} · vizinhos/relação: {vis['max_neighbors']} · "
               f"{len(vis['nodes'])} nós, {len(vis['edges'])} arestas.")
            if HAS_GRAPH:
                png = os.path.splitext(filename)[0] + ".graph.png"
                ap(f"![grafo]({os.path.basename(png)})" if markdown
                   else f"Imagem do grafo: {os.path.basename(png)}")
            lab = {n["id"]: n.get("label") or n["id"] for n in vis["nodes"]}
            ap("")
            ap("Arestas:" if not markdown else "**Arestas:**")
            for e in vis["edges"]:
                ap(f"{BUL}{lab.get(e['source'], e['source'])} "
                   f"—[{e['rel_label']}]→ {lab.get(e['target'], e['target'])}")

        text = "\n".join(L) + "\n"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)

    def _export_graph_png(self, filename):
        """Grava apenas a imagem do grafo."""
        if not HAS_GRAPH:
            raise RuntimeError("matplotlib/networkx não instalados — PNG indisponível.")
        graph_type = getattr(self, "graph_type", None) and self.graph_type.get() or "Todos"
        max_neighbors = (getattr(self, "graph_neighbors", None)
                         and self.graph_neighbors.get()) or 4
        fig = self._build_graph_figure(graph_type, max_neighbors)
        if fig is None:
            raise RuntimeError("Nenhum nó para desenhar (grafo vazio).")
        try:
            fig.savefig(filename, dpi=150, bbox_inches="tight")
        finally:
            plt.close(fig)

    def _maybe_export_graph_sidecar(self, filename) -> list:
        """Grava `<nome>.graph.png` ao lado de um relatório, se possível."""
        if not HAS_GRAPH:
            return []
        png = os.path.splitext(filename)[0] + ".graph.png"
        try:
            self._export_graph_png(png)
            return [png]
        except Exception:
            return []


# ---------- Execução Principal ----------
if __name__ == "__main__":
    print("="*60)
    print("Open English Wordnet GUI - Iniciando...")
    print("="*60)
    
    # Teste rápido do WordNet
    try:
        test = wn.synsets('dog')
        if test:
            print("✓ Open English Wordnet funcionando corretamente")
            print(f"  Exemplo: 'dog' tem {len(test)} synsets")
        else:
            print("⚠ Open English Wordnet carregado mas pode ter problemas")
    except Exception as e:
        print(f"✗ Erro ao testar Open English Wordnet: {e}")
        print("\nTente executar:")
        print("  pip install wn")
        print("  python -c \"import wn; wn.download('oewn:2024')\"")
        response = messagebox.askyesno(
            "Erro",
            "Open English Wordnet não está funcionando.\n\n"
            "Deseja tentar descarregar os dados agora?",
        )
        if response:
            try:
                ensure_oewn()
            except Exception:
                pass
    
    print("\nIniciando interface gráfica...")
    print("-"*60)
    
    try:
        app = WordNetCompleteGUI()
        app.mainloop()
    except Exception as e:
        print(f"Erro fatal: {e}")
        messagebox.showerror("Erro Fatal", f"Não foi possível iniciar o GUI:\n{e}")