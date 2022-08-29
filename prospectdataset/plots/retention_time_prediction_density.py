import sys
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.ticker import LogLocator

parser = argparse.ArgumentParser()
parser.add_argument(
    "-p",
    "--pred_path",
    help="Path to the file with Retention time predictions and targets"
)

parser.add_argument(
    "-d",
    "--delta_95",
    help="iRT delta95 value"
)


def main(sys_args=sys.argv[1:]):
    args = parser.parse_args(sys_args)
    iRT_pred_targets = pd.read_parquet(args.pred_path)
    plot_density(iRT_pred_targets['targets'], iRT_pred_targets['predictions'], args.delta_95)

def plot_density(
        targets,
        predictions,
        irt_delta95=5,
        palette="Reds_r",
        delta95_line_color="#36479E",
        nbins=1000,
):
    """Create density plot
    Arguments
    ---------
        targets:  Array with target values
        predictions:  Array with prediction values
        irt_delta95 (int, optional): iRT Value of the delta 95% . Defaults to 5.
        palette (str, optional): Color palette from matplotlib. Defaults to 'Reds_r'.
        delta95_line_color (str, optional): Color for the delta 95% line. Defaults to '#36479E'.
        nbins (int, optional): Number of bins to use for creating the 2D histogram. Defaults to 1000.
    """

    H, xedges, yedges = np.histogram2d(targets, predictions, bins=nbins)

    x_min = np.min(targets)
    x_max = np.max(targets)

    # H needs to be rotated and flipped
    H = np.rot90(H)
    H = np.flipud(H)

    # Mask zeros
    Hmasked = np.ma.masked_where(H == 0, H)  # Mask pixels with a value of zero

    # Plot 2D histogram using pcolor
    cm = plt.cm.get_cmap(palette)
    plt.pcolormesh(
        xedges, yedges, Hmasked, cmap=cm, norm=LogNorm(vmin=1e0, vmax=1e2)
    )

    plt.xlabel('Targets', fontsize=18)
    plt.ylabel('Predictions', fontsize=18)

    cbar = plt.colorbar(ticks=LogLocator(subs=range(5)))
    cbar.ax.set_ylabel("Counts", fontsize=14)

    plt.plot([x_min, x_max], [x_min, x_max], c="black")
    plt.plot(
        [x_min, x_max],
        [x_min - irt_delta95, x_max - irt_delta95],
        color=delta95_line_color,
    )
    plt.plot(
        [x_min, x_max],
        [x_min + irt_delta95, x_max + irt_delta95],
        color=delta95_line_color,
    )

    font_size = 14  # Adjust as appropriate.
    cbar.ax.tick_params(labelsize=font_size)
    cbar.ax.minorticks_on()
    plt.savefig('iRT_density_plot.svg')
    plt.show()
    plt.close()
