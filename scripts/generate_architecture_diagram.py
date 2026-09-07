import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, PathPatch
from matplotlib.path import Path

def create_diagram(output_path: str):
    fig, ax = plt.subplots(figsize=(12.0, 9.6), dpi=120)
    ax.set_xlim(0, 1200)
    ax.set_ylim(0, 960)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    def draw_box(x, y, w, h, text, subtitle=None, bg_color="#FFFFFF", border_color="#333333", linestyle="-", linewidth=1.5, boxstyle="round,pad=0.5,rounding_size=10"):
        box = FancyBboxPatch((x, y), w, h, boxstyle=boxstyle,
                             facecolor=bg_color, edgecolor=border_color,
                             linestyle=linestyle, linewidth=linewidth)
        ax.add_patch(box)
        cx = x + w / 2
        if subtitle:
            cy = y + h / 2 + 10
            ax.text(cx, cy, text, ha="center", va="center", fontsize=10.5, fontweight="bold", color="#111111", fontfamily="sans-serif")
            ax.text(cx, cy - 20, subtitle, ha="center", va="center", fontsize=9, color="#555555", fontfamily="sans-serif")
        else:
            cy = y + h / 2
            ax.text(cx, cy, text, ha="center", va="center", fontsize=10.5, fontweight="bold", color="#111111", fontfamily="sans-serif")

    def draw_cylinder(x, y, w, h, title, subtitle=None, bg_color="#F8F9FA", border_color="#333333", linestyle="-"):
        ellipse_h = 14
        path_data = [
            (Path.MOVETO, (x, y + ellipse_h)),
            (Path.LINETO, (x, y + h - ellipse_h)),
            (Path.CURVE4, (x, y + h)),
            (Path.CURVE4, (x + w, y + h)),
            (Path.CURVE4, (x + w, y + h - ellipse_h)),
            (Path.LINETO, (x + w, y + ellipse_h)),
            (Path.CURVE4, (x + w, y)),
            (Path.CURVE4, (x, y)),
            (Path.CURVE4, (x, y + ellipse_h)),
            (Path.CLOSEPOLY, (x, y + ellipse_h))
        ]
        codes, verts = zip(*path_data)
        path = Path(verts, codes)
        patch = PathPatch(path, facecolor=bg_color, edgecolor=border_color, linestyle=linestyle, linewidth=1.5)
        ax.add_patch(patch)
        top_path_data = [
            (Path.MOVETO, (x, y + h - ellipse_h)),
            (Path.CURVE4, (x, y + h - 2 * ellipse_h)),
            (Path.CURVE4, (x + w, y + h - 2 * ellipse_h)),
            (Path.CURVE4, (x + w, y + h - ellipse_h)),
        ]
        t_codes, t_verts = zip(*top_path_data)
        t_patch = PathPatch(Path(t_verts, t_codes), facecolor="none", edgecolor=border_color, linestyle=linestyle, linewidth=1.5)
        ax.add_patch(t_patch)
        cx = x + w / 2
        cy = y + h / 2 - 4
        if subtitle:
            ax.text(cx, cy + 9, title, ha="center", va="center", fontsize=10, fontweight="bold", color="#111111", fontfamily="sans-serif")
            ax.text(cx, cy - 13, subtitle, ha="center", va="center", fontsize=8.5, color="#555555", fontfamily="sans-serif")
        else:
            ax.text(cx, cy, title, ha="center", va="center", fontsize=10, fontweight="bold", color="#111111", fontfamily="sans-serif")

    def draw_document(x, y, w, h, title, subtitle=None, bg_color="#FFFFFF", border_color="#333333"):
        wave_h = 8
        path_data = [
            (Path.MOVETO, (x, y + wave_h)),
            (Path.LINETO, (x, y + h)),
            (Path.LINETO, (x + w, y + h)),
            (Path.LINETO, (x + w, y + wave_h)),
            (Path.CURVE4, (x + w * 0.75, y - wave_h * 0.5)),
            (Path.CURVE4, (x + w * 0.5, y + wave_h * 1.5)),
            (Path.CURVE4, (x, y + wave_h)),
            (Path.CLOSEPOLY, (x, y + wave_h))
        ]
        codes, verts = zip(*path_data)
        patch = PathPatch(Path(verts, codes), facecolor=bg_color, edgecolor=border_color, linewidth=1.5)
        ax.add_patch(patch)
        cx = x + w / 2
        cy = y + h / 2 + 2
        if subtitle:
            ax.text(cx, cy + 10, title, ha="center", va="center", fontsize=10, fontweight="bold", color="#111111", fontfamily="sans-serif")
            ax.text(cx, cy - 12, subtitle, ha="center", va="center", fontsize=8.5, color="#555555", fontfamily="sans-serif")
        else:
            ax.text(cx, cy, title, ha="center", va="center", fontsize=10, fontweight="bold", color="#111111", fontfamily="sans-serif")

    # Outer platform boundary
    platform_box = FancyBboxPatch((230, 205), 680, 715, boxstyle="round,pad=0.8,rounding_size=20",
                                  facecolor="#FAFAFB", edgecolor="#777777", linestyle="--", linewidth=1.8)
    ax.add_patch(platform_box)
    ax.text(570, 895, "BiasAperture Platform", ha="center", va="center", fontsize=14, fontweight="bold", color="#111111", fontfamily="sans-serif")

    # 1. Orchestration Layer (argparse CLI)
    draw_box(265, 805, 610, 60, "Orchestration Layer — CLI (argparse)", "Declarative execution flags: --backend [dual|fairlearn|aif360], --bca-resamples")

    # 2. Data Ingestion & Model Interface Modules
    draw_box(265, 650, 260, 105, "Data Ingestion &", "Alignment Module\n(FairFace 97,698 Ingestion)")
    draw_box(615, 650, 260, 105, "Model Interface", "Module\n(PredictionsFile & InProcess)")

    # 3. Fairness Metrics Engine (AIF360 & Fairlearn)
    engine_box = FancyBboxPatch((265, 425), 610, 165, boxstyle="round,pad=0.6,rounding_size=14",
                                facecolor="#FFFFFF", edgecolor="#333333", linewidth=1.5)
    ax.add_patch(engine_box)
    ax.text(570, 562, "Fairness Metrics Engine", ha="center", va="center", fontsize=12, fontweight="bold", color="#111111", fontfamily="sans-serif")
    ax.text(570, 542, "CrossValidationOrchestrator: Dual-Backend Verification (NFR-001, NFR-002)", ha="center", va="center", fontsize=9, color="#666666", fontfamily="sans-serif")
    draw_box(315, 446, 200, 70, "AIF360", "Core Four Strategy")
    draw_box(625, 446, 200, 70, "Fairlearn", "Core Four Strategy")

    # 4. Explainability Layer & Report Generation Module
    explain_box = FancyBboxPatch((265, 235), 265, 145, boxstyle="round,pad=0.6,rounding_size=14",
                                 facecolor="#FFFFFF", edgecolor="#333333", linewidth=1.5)
    ax.add_patch(explain_box)
    ax.text(397, 355, "Explainability Layer", ha="center", va="center", fontsize=11, fontweight="bold", color="#111111", fontfamily="sans-serif")
    draw_box(280, 255, 235, 75, "Surrogate Attribution", "Linear Shapley on Disparities\n(Spatial SHAP Deferred)")

    report_box = FancyBboxPatch((610, 235), 265, 145, boxstyle="round,pad=0.6,rounding_size=14",
                                facecolor="#FFFFFF", edgecolor="#333333", linewidth=1.5)
    ax.add_patch(report_box)
    ax.text(742, 355, "Report Generation Module", ha="center", va="center", fontsize=11, fontweight="bold", color="#111111", fontfamily="sans-serif")
    draw_box(622, 260, 115, 68, "Jinja2", "Zero-Network\nHTML Dossier")
    draw_box(748, 260, 115, 68, "Model Cards", "& Datasheets\nConventions")

    # Left external inputs: Datasets
    draw_cylinder(25, 760, 175, 95, "FairFace Dataset", "97,698 images (released)\n86,744 train | 10,954 val", bg_color="#EEF6FF", border_color="#2563EB")
    draw_cylinder(25, 625, 175, 95, "UTKFace Dataset", "[CUT, Cut-List #2]\nProfiled only, not ingested", bg_color="#FFF1F2", border_color="#DC2626", linestyle=":")

    # Right external inputs: Model Inputs
    draw_document(940, 750, 235, 95, "PyTorch / TensorFlow", "In-Process Model Object\n(predict() interface)")
    draw_document(940, 620, 235, 95, "Black-Box Model Output", "Predictions File (CSV / JSON)\nFramework-Agnostic")

    # Downstream Output: Compliance Report (HTML) - at x=435, y=112 (w=270, h=58)
    draw_box(435, 112, 270, 58, "Compliance Report (HTML)", "Zero-network offline verifiable audit report", bg_color="#F0FDF4", border_color="#16A34A")

    # Regulatory traceability footer - at x=305, y=20 (w=530, h=50)
    draw_document(305, 20, 530, 50, "Regulatory Traceability & Audit Manifest", "EU AI Act Art. 10 / Annex IV · NIST AI RMF 1.0 (Measure 1.1, 1.3, 2.11) · manifest.json")

    # Arrows & Connections
    arrow_kw = dict(arrowstyle="->", color="#333333", lw=1.5)
    dashed_arrow_kw = dict(arrowstyle="->", color="#666666", lw=1.3, linestyle="--")

    # CLI to Ingestion and Interface (dashed control)
    ax.annotate("", xy=(395, 755), xytext=(395, 805), arrowprops=dashed_arrow_kw)
    ax.annotate("", xy=(745, 755), xytext=(745, 805), arrowprops=dashed_arrow_kw)

    # Datasets to Ingestion
    ax.annotate("", xy=(265, 710), xytext=(200, 805), arrowprops=arrow_kw)
    ax.annotate("", xy=(265, 690), xytext=(200, 670), arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.3, linestyle=":"))

    # Models to Model Interface
    ax.annotate("", xy=(875, 710), xytext=(940, 795), arrowprops=arrow_kw)
    ax.annotate("", xy=(875, 690), xytext=(940, 665), arrowprops=arrow_kw)

    # Ingestion & Interface down to Fairness Engine
    ax.annotate("", xy=(395, 590), xytext=(395, 650), arrowprops=arrow_kw)
    ax.annotate("", xy=(745, 590), xytext=(745, 650), arrowprops=arrow_kw)

    # Engine down to Explainability & Report
    ax.plot([570, 570], [425, 310], color="#333333", lw=1.5)
    ax.annotate("", xy=(530, 310), xytext=(570, 310), arrowprops=arrow_kw)
    ax.annotate("", xy=(610, 310), xytext=(570, 310), arrowprops=arrow_kw)

    # Explainability <-> Report communication
    ax.annotate("", xy=(610, 290), xytext=(530, 290), arrowprops=dict(arrowstyle="<->", color="#555555", lw=1.3))

    # Report down to Compliance Report HTML: from bottom center of report_box (x=742, y=235) down to y=141, then horizontally to right edge of compliance box (x=705, y=141)
    ax.plot([742, 742], [235, 141], color="#333333", lw=1.5)
    ax.plot([742, 706], [141, 141], color="#333333", lw=1.5)
    ax.annotate("", xy=(705, 141), xytext=(715, 141), arrowprops=arrow_kw)

    # Compliance Report down to Regulatory Manifest: from bottom of compliance box (x=570, y=112) down to top of manifest (x=570, y=70)
    ax.plot([570, 570], [112, 75], color="#333333", lw=1.5)
    ax.annotate("", xy=(570, 70), xytext=(570, 78), arrowprops=arrow_kw)

    plt.tight_layout()
    plt.savefig(output_path, dpi=120, format="jpg")
    plt.close()
    print(f"Successfully generated clean architecture diagram: {output_path}")

if __name__ == "__main__":
    create_diagram("report/src/images/architecture_highlevel.jpg")
