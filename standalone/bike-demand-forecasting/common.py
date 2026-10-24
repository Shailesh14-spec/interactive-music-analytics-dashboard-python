from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'reports'
OUT.mkdir(exist_ok=True)
def save_json(name, obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,default=lambda x:x.item())+'\n')
def save_chart(fig,name):
    fig.tight_layout()
    fig.savefig(OUT/(name+'.svg'))
    fig.savefig(OUT/(name+'.png'),dpi=130)
    plt.close(fig)
