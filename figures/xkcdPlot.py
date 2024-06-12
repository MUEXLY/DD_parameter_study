import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager

with plt.xkcd():
    # Path to your custom font file
    font_path = '/usr/share/fonts/TTF/xkcd-script.ttf'
    # Add the custom font to Matplotlib's font manager
    font_manager.fontManager.addfont(font_path)
    # Set the font family globally to your custom font
    plt.rcParams['font.family'] = 'xkcd Script'

    fig = plt.figure()
    ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_ylim([-1, 10])

    someDataX, someDataY = np.linspace(0, 10, 100), np.linspace(0, 10, 100)
    xrng = 50
    noise1 = (np.random.rand(xrng)-0.5)*0.2          # sensor noise

    ax.plot(someDataX, someDataY)
    meanLow, meanHigh = 4, 6
    ax.axhline(y=meanLow, color='r', linestyle='--')  # Red solid line at y=2
    ax.axhline(y=meanHigh, color='g', linestyle='--') # Green dashed line at y=3
    ax.annotate( 'perhaps way too low', xy=(5, meanLow), arrowprops=dict(arrowstyle='->'), xytext=(3, 2))
    ax.annotate( 'perhaps way too high', xy=(5, meanHigh), arrowprops=dict(arrowstyle='->'), xytext=(2, 7))
    ax.annotate( 'CRSS is around here', xy=(5, (meanLow+meanHigh)/2), arrowprops=dict(arrowstyle='->'), xytext=(7, 5))

    ax.set_xlabel('Applied Stress')
    ax.set_ylabel('Mean of betaP')
    fig.text(
        0.5, 0.05,
        '"Super rigorous way to find the energy barrier\n of the depinning transition"',
        ha='center')
    fig.savefig('CRSSsearch.png', bbox_inches='tight', dpi=150)

plt.xkcd()
