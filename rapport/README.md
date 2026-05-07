# Rapport LaTeX - Plateforme Big Data d'Analyse de Médias

## 📄 Structure

```
rapport/
├── main.tex              # Fichier principal (tous les chapitres)
├── references.bib        # Bibliographie
├── README.md            # Ce fichier
└── output/              # Dossier de sortie (créé après compilation)
    └── main.pdf         # Rapport PDF généré
```

## 🛠️ Prérequis

### Windows

#### Option 1: MiKTeX (Recommandé pour Windows)

```powershell
# Installation via Chocolatey
choco install miktex

# Ou télécharger depuis: https://miktex.org/download
```

#### Option 2: TeX Live

```powershell
# Installation via Chocolatey
choco install texlive
```

#### Option 3: Overleaf (En ligne)

- Aller sur https://www.overleaf.com
- Créer un nouveau projet
- Uploader les fichiers `main.tex` et `references.bib`
- Compiler directement en ligne

### Linux

```bash
# Ubuntu/Debian
sudo apt-get install texlive-latex-base texlive-fonts-recommended texlive-latex-extra texlive-xetex

# Ou installation complète
sudo apt-get install texlive-full
```

### macOS

```bash
# Via Homebrew
brew install mactex

# Ou via MacPorts
sudo port install texlive +full
```

## 📖 Compilation

### Option 1: Ligne de commande (PowerShell Windows)

```powershell
# Naviguer vers le dossier rapport
cd C:\Users\hp\Desktop\projet_news_bigdata\rapport

# Compilation basique (1 pass)
pdflatex -interaction=nonstopmode main.tex

# Compilation avec biblio (3 passes)
pdflatex -interaction=nonstopmode main.tex
bibtex main.aux
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

# Clean files
del *.aux *.log *.out *.toc *.bbl *.blg 2>$null
```

### Option 2: VS Code (Recommandé)

1. **Installer l'extension LaTeX Workshop**
   - Ctrl+Shift+X → Chercher "LaTeX Workshop"
   - Installer par James Yu

2. **Configurer**
   - Ouvrir settings.json (Ctrl+,)
   - Ajouter:

   ```json
   "latex-workshop.latex.tools": [
       {
           "name": "pdflatex",
           "command": "pdflatex",
           "args": ["-interaction=nonstopmode", "-synctex=1", "%DOC%"]
       },
       {
           "name": "bibtex",
           "command": "bibtex",
           "args": ["%DOCFILE%"]
       }
   ],
   "latex-workshop.latex.recipes": [
       {
           "name": "pdflatex → bibtex → pdflatex × 2",
           "tools": ["pdflatex", "bibtex", "pdflatex", "pdflatex"]
       }
   ]
   ```

3. **Compiler**
   - Ctrl+Alt+B (build) ou Ctrl+S (save & build)
   - Voir PDF en prévisualisation (Ctrl+Alt+V)

### Option 3: Overleaf (En ligne, pas d'installation)

1. Allez sur https://www.overleaf.com
2. Créer un nouveau projet
3. Copier-coller contenu de `main.tex`
4. Créer fichier `references.bib`
5. Compiler directement

### Option 4: Script PowerShell (Automatisé)

Créer fichier `compile.ps1`:

```powershell
# Compilation automatisée
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $dir

Write-Host "Compiling LaTeX..." -ForegroundColor Green

# 3 passes de pdflatex + bibtex
pdflatex -interaction=nonstopmode main.tex | Out-Null
bibtex main.aux | Out-Null
pdflatex -interaction=nonstopmode main.tex | Out-Null
pdflatex -interaction=nonstopmode main.tex | Out-Null

Write-Host "Compilation terminée!" -ForegroundColor Green
Write-Host "PDF généré: main.pdf" -ForegroundColor Yellow

# Cleanup
Remove-Item *.aux, *.log, *.out, *.toc, *.bbl, *.blg, *.synctex.gz -ErrorAction SilentlyContinue

Write-Host "Fichiers temporaires supprimés." -ForegroundColor Green
```

Puis exécuter:

```powershell
.\compile.ps1
```

## 📑 Fichiers Générés

Après compilation:

```
main.pdf              # ← Rapport final (télécharger/ouvrir)
main.aux              # Auxiliaire (supprimé)
main.log              # Log compilation (supprimé)
main.toc              # Table des matières (supprimé)
main.bbl              # Bibliographie compilée (supprimé)
```

## ✏️ Éditer le Rapport

### Ajouter un chapitre

Dans `main.tex`, avant `\end{document}`:

```latex
\chapter{Nouveau Chapitre}

\section{Première section}

Contenu du rapport...

\subsection{Sous-section}

Plus de contenu...
```

### Ajouter une figure

```latex
\begin{figure}[H]
\centering
\includegraphics[width=0.8\textwidth]{chemin/vers/image.png}
\caption{Légende de la figure}
\label{fig:etiquette}
\end{figure}

Référencer: Voir la Figure~\ref{fig:etiquette}.
```

### Ajouter un tableau

```latex
\begin{table}[H]
\centering
\begin{tabular}{lll}
\toprule
\textbf{Colonne 1} & \textbf{Colonne 2} & \textbf{Colonne 3} \\
\midrule
Ligne 1 & Valeur & Données \\
Ligne 2 & Valeur & Données \\
\bottomrule
\end{tabular}
\caption{Légende du tableau}
\end{table}
```

### Ajouter une référence bibliographique

1. Ajouter dans `references.bib`:

```bibtex
@book{auteur2023,
    author = {Auteur, Nom},
    title = {Titre du Livre},
    publisher = {Éditeur},
    year = {2023}
}
```

2. Citer dans le texte:

```latex
Selon~\cite{auteur2023}, ...
```

## 🔧 Troubleshooting

### Erreur: "pdflatex not found"

- Vérifier installation de MiKTeX/TeX Live
- Ajouter au PATH: `C:\Program Files\MiKTeX\miktex\bin\x64`

### Erreur: "Unable to find a template"

- VS Code LaTeX Workshop: Ctrl+Shift+P → "LaTeX Workshop: View PDF file"

### La bibliographie ne s'affiche pas

- S'assurer que `references.bib` est dans le même dossier
- Recompiler 3 fois: `pdflatex → bibtex → pdflatex → pdflatex`

### Caractères spéciaux mal affichés

- Vérifier l'encoding UTF-8
- Ou utiliser `\usepackage[utf-8]{inputenc}` (déjà présent)

### PDF trop grand

- Compresser:

```powershell
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH -sOutputFile=main_compressed.pdf main.pdf
```

## 📊 Structure du Document

- **Frontmatter**: Page de titre, toc, résumé
- **10 Chapitres**: Introduction → Conclusion
- **Appendices**: Références, annexes
- **Backmatter**: Bibliographie

### Chapitres Inclus

1. Introduction
2. État de l'Art
3. Problématique & Spécifications
4. Architecture
5. Implémentation
6. Résultats
7. Tests & Validation
8. Déploiement
9. Limitations & Perspectives
10. Conclusion

## 📝 Conseils de Rédaction

- **Utiliser des sections** pour structurer
- **Références croisées**: `\label{} / \ref{}`
- **Italique pour emphase**: `\textit{texte}`
- **Bold pour importance**: `\textbf{texte}`
- **Listes ordonnées**: `\begin{enumerate} / \end{enumerate}`
- **Listes non-ordonnées**: `\begin{itemize} / \end{itemize}`

## 🎨 Personnalisation

### Changer couleur principale

Dans `main.tex`, remplacer:

```latex
\definecolor{darkblue}{RGB}{0, 102, 204}
```

Par exemple:

- Vert: `RGB}{0, 128, 0}`
- Rouge: `RGB}{192, 0, 0}`
- Noir: `RGB}{0, 0, 0}`

### Changer police

Ajouter avant `\begin{document}`:

```latex
\usepackage{times}              % Times New Roman
\usepackage{palatino}           % Palatino
\usepackage{helvet}             % Helvetica
```

### Numérotation personnalisée

```latex
\pagenumbering{roman}           % Pages i, ii, iii, ...
\pagenumbering{arabic}          % Pages 1, 2, 3, ... (défaut)
```

## 📥 Export Formats

### PDF (par défaut)

```powershell
pdflatex -interaction=nonstopmode main.tex
```

### HTML (avec pandoc)

```powershell
choco install pandoc
pandoc main.tex -o main.html
```

### DOCX (Microsoft Word)

```powershell
pandoc main.tex -o main.docx
```

## 🚀 Prochaines Étapes

1. **Éditer et enrichir** le contenu des chapitres
2. **Ajouter des images** (diagrams, screenshots)
3. **Corriger l'orthographe** et la grammaire
4. **Compiler en PDF** une fois terminé
5. **Vérifier les références** croisées et bibliographie

## 📞 Support

- LaTeX Help: https://www.overleaf.com/learn
- Stack Exchange LaTeX: https://tex.stackexchange.com/
- LaTeX Workshop Docs: https://github.com/James-Yu/LaTeX-Workshop

---

**Bonne rédaction!** ✍️
