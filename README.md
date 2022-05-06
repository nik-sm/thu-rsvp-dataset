# Tsinghua University RSVP Benchmark Dataset

This repo provides Python code for loading publicly-available data from **A Benchmark Dataset for RSVP-Based Brain–Computer Interfaces** by Shangen Zhang, Yijun Wang, Lijian Zhang, and Xiaorong Gao. Note that this repo is not affiliated or endorsed by the authors.

See the full paper at: https://www.frontiersin.org/articles/10.3389/fnins.2020.568000/full

Abstract:
> This paper reports on a benchmark dataset acquired with a brain–computer interface (BCI) system based on the rapid serial visual presentation (RSVP) paradigm. The dataset consists of 64-channel electroencephalogram (EEG) data from 64 healthy subjects (sub1,..., sub64) while they performed a target image detection task. For each subject, the data contained two groups ("A" and "B"). Each group contained two blocks, and each block included 40 trials that corresponded to 40 stimulus sequences. Each sequence contained 100 images presented at 10 Hz (10 images per second). The stimulus images were street-view images of two categories: target images with human and non-target images without human. Target images were presented randomly in the stimulus sequence with a probability of 1∼4%. During the stimulus presentation, subjects were asked to search for the target images and ignore the non-target images in a subjective manner. To keep all original information, the dataset was the raw continuous data without any processing. On one hand, the dataset can be used as a benchmark dataset to compare the algorithms for target identification in RSVP-based BCIs. On the other hand, the dataset can be used to design new system diagrams and evaluate their BCI performance without collecting any new data through offline simulation. Furthermore, the dataset also provides high-quality data for characterizing and modeling event-related potentials (ERPs) and steady-state visual evoked potentials (SSVEPs) in RSVP-based BCIs. The dataset is freely available from http://bci.med.tsinghua.edu.cn/download.html.

Citation:
```
@article{zhang2020benchmark,
  title={A benchmark dataset for RSVP-based brain--computer interfaces},
  author={Zhang, Shangen and Wang, Yijun and Zhang, Lijian and Gao, Xiaorong},
  journal={Frontiers in Neuroscience},
  pages={1042},
  year={2020},
  publisher={Frontiers}
}
```

# Setup

Install from PyPI with:
```shell
pip install thu-rsvp-dataset
```

Or install from github with:
```shell
git clone https://github.com/nik-sm/thu-rsvp-dataset.git
cd thu-rsvp-dataset
python3 -m venv venv
source venv/bin/activate
venv/bin/pip install -Ue .
```

# Usage 

See [load_dataset.py](examples/load_dataset.py) for example usage.