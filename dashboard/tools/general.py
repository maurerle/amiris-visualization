import pathlib as pt
import importlib

import qrcode


def create_qrcode(url: str):
    img = qrcode.make(url)
    return img.get_image()


def load_tab_modules():
    tab_hooks = {}

    for i in pt.Path("./tabs").glob("tab_*.py"):
        spec = importlib.util.spec_from_file_location(f"dashboard.tabs.{i.stem}", i)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        tab_hooks[i.stem[4:]] = mod

    return tab_hooks
