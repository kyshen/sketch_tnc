from pathlib import Path

import hydra
from omegaconf import DictConfig

from src.runner import run_experiment


@hydra.main(config_path="configs", config_name="config", version_base=None)
def main(cfg: DictConfig):
    out_dir = run_experiment(cfg)
    return Path(out_dir)


if __name__ == "__main__":
    main()
