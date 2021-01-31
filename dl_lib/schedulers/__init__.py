import logging
from typing import Dict, Any
from copy import deepcopy

from torch.optim.lr_scheduler import MultiStepLR, ExponentialLR, CosineAnnealingLR

from .schedulers import WarmUpLR, ConstantLR, PolynomialLR
from dl_lib.utils import to_json_str


__REGISTERED_SCHEDULERS__ = {
    "constant_lr": ConstantLR,
    "poly_lr": PolynomialLR,
    "multi_step": MultiStepLR,
    "cosine_annealing": CosineAnnealingLR,
    "exp_lr": ExponentialLR,
}


def get_scheduler(optimizer, scheduler_cfg: Dict[str, Dict[str, Any]]):
    """
    scheduler yml example
    ```
        lr_schedule:
            name: multi_step
            milestones: [8000]
            gamma: 0.1
    ```
    """
    logger = logging.getLogger("get_scheduler")

    scheduler_dict = deepcopy(scheduler_cfg)
    if scheduler_dict is None:
        logger.info("Using No lr scheduling, fallback to constant lr")
        return ConstantLR(optimizer)

    s_type = scheduler_dict.pop("name")

    logging.info("Using {} scheduler with\n{}".format(s_type, to_json_str(scheduler_dict)))

    if "warmup_iters" in scheduler_dict:
        warmup_dict = {}
        warmup_dict["warmup_iters"] = scheduler_dict.pop("warmup_iters", 100)
        warmup_dict["mode"] = scheduler_dict.pop("warmup_mode", "linear")
        warmup_dict["gamma"] = scheduler_dict.pop("warmup_factor", 0.2)

        logger.info(
            "Using Warmup with {} iters {} gamma and {} mode".format(
                warmup_dict["warmup_iters"], warmup_dict["gamma"], warmup_dict["mode"]
            )
        )

        base_scheduler = __REGISTERED_SCHEDULERS__[s_type](optimizer, **scheduler_dict)
        return WarmUpLR(optimizer, base_scheduler, **warmup_dict)

    return __REGISTERED_SCHEDULERS__[s_type](optimizer, **scheduler_dict)
