# Adapted from https://github.com/molecularsets/moses/blob/master/scripts/vae/train.py
from copy import deepcopy
import logging
import os
import torch

from moses.script_utils import add_train_args, set_seed
from moses.vae.config import get_parser as vae_parser
from moses.vae.corpus import OneHotCorpus
from moses.vae.model import VAE
from moses.vae.trainer import VAETrainer

from .common import read_smiles

logger = logging.getLogger(__name__)


def get_parser():
    return add_train_args(vae_parser())


def main(config):
    set_seed(config.seed)

    train = read_smiles(config.train_load)

    device = torch.device(config.device)

    # For CUDNN to work properly:
    if device.type.startswith('cuda'):
        torch.cuda.set_device(device.index or 0)

    corpus = OneHotCorpus(config.n_batch, device)
    train = corpus.fit(train).transform(train)

    if config.warm_start:
        logger.warning(
            f"Warmstarting model from {config.warm_start} "
            "This overrides all model configuration parameters. "
        )
        model_config = torch.load(os.path.join(config.warm_start, "config.pt"))
        model_vocab = torch.load(os.path.join(config.warm_start, "vocab.pt"))
        for k, v in corpus.vocab.c2i.items():
            if model_vocab.c2i.get(k) != v:
                raise ValueError(
                    f"Vocab mismatch - NEW: {k}: {v}; OLD: {model_vocab.c2i.get(k)}"
                )
    else:
        model_config = deepcopy(config)
        model_vocab = deepcopy(corpus.vocab)

    model = VAE(model_vocab, model_config).to(device)
    if config.warm_start:
        model.load(
            path=os.path.join(config.warm_start, "model.pt"), map_location=config.device
        )
        logger.warning(f"Loaded model from {config.warm_start}")

    trainer = VAETrainer(config)

    torch.save(config, config.config_save)
    torch.save(model_vocab, config.vocab_save)
    trainer.fit(model, train)


if __name__ == '__main__':
    parser = get_parser()
    config = parser.parse_known_args()[0]
    main(config)
