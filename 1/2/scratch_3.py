
import jinja2
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, FileLink

# Create template with TikZ annotations
template_content1 = r"""
\documentclass[12pt]{article}
\usepackage{graphicx}
\usepackage{tikz}
\usepackage{booktabs}
\usepackage{amsmath}

\begin{document}
\title{\LARGE\textbf{<< title >>}}
\author{\textit{<< author >>}}
\date{\small\today}
\maketitle

\begin{figure}[h]
    \centering
    \begin{tikzpicture}
        \node[anchor=south west] (image) at (0,0) {
            \includegraphics[width=0.95\textwidth]{<< plot_path >>}
        };

        \begin{scope}[x={(image.south east)}, y={(image.north west)}]
            << tikz_annotations >>
        \end{scope}
    \end{tikzpicture}
    \caption{\small << plot_caption >>}
\end{figure}

<< analysis_section >>

\end{document}
"""

with open('report_template1.tex', 'w') as f:
    f.write(template_content1)

# Generate clean base plot
plt.figure(figsize=(10, 6))
x = [1, 2, 3, 4]
y = [1, 4, 9, 16]
plt.plot(x, y, 'b-o', linewidth=2)
plt.title('Base Data Plot', fontsize=12)
plt.xlabel('X Axis')
plt.ylabel('Y Axis')
plt.grid(True, alpha=0.3)
plt.savefig('figure.png', bbox_inches='tight', dpi=300)
plt.close()

# Define TikZ annotations
tikz_annotations = r"""
% Diagonal trend line
\draw[blue, thick, dashed] (0.15,0.85) -- (0.85,0.15);

% Vertical reference line
\draw[blue, thick, opacity=0.7] (0.5,0) -- (0.5,1);

% Text annotation
\node[draw=black, fill=yellow, align=left] at (0.3,0.7) {
    \scriptsize Key Growth\\Phase
};
\draw[->, thick] (0.3,0.7) -- (0.4,0.6);

% Data point highlight
\draw[orange, thick] (0.75,0.25) circle [radius=0.07];

% Measurement arrow
\draw[<->, thick, purple] (0.2,0.2) -- node[midway, below] {\small Critical Range} (0.8,0.2);
"""

context1 = {
    "title": "Annotated Visualization Report",
    "author": "Data Team",
    "plot_path": "figure.png",
    "plot_caption": "Base plot with LaTeX-generated annotations",
    "tikz_annotations": tikz_annotations,
    "analysis_section": r"""
    \begin{itemize}
        \item Red dashed line shows expected trend
        \item Blue line marks midpoint
        \item Yellow box highlights key phase
        \item Orange circle indicates outlier
    \end{itemize}
    """
}

# Jinja2 setup
template_loader = jinja2.FileSystemLoader(searchpath="./")
template_env = jinja2.Environment(
    loader=template_loader,
    block_start_string='{%',
    block_end_string='%}',
    variable_start_string='<<',
    variable_end_string='>>'
)

template = template_env.get_template("report_template1.tex")
output = template.render(context1)

with open("generated_report1.tex", "w") as f:
    f.write(output)

# Compile to PDF
import subprocess

subprocess.run(["pdflatex", "-interaction=nonstopmode", "generated_report1.tex"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["pdflatex", "-interaction=nonstopmode", "generated_report1.tex"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Отображение PDF

display(FileLink('generated_report1.pdf'))
