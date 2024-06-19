# SPDX-FileCopyrightText: 2024 German Aerospace Center
#
# SPDX-License-Identifier: Apache-2.0
import collections
import json
import pathlib as pt

import cattr
from attr import define, field

# cattr hooks
cattr.register_structure_hook(pt.Path, lambda i, t: t(i))
cattr.register_unstructure_hook(pt.Path, lambda i: i.as_posix())


@define
class TabData:
    id: str = field()
    label: str = field(default="tab")
    icon: str = field(default="bar-chart")
    text: str | None = field(default=None)
    path: pt.Path | None = field(default=None)
    display_infobox: bool = field(default=False)
    display_label: str = field(default="do you want to know more?")
    display_icon: str = field(default=":grey_question:")
    display_enabled: bool = field(default=True)

    tab_ref: None = field(default=None)


@define
class DashboardConfiguration:
    enable_darkmode_toggle: bool = field(default=True)
    enable_references: bool = field(default=True)
    tabs: list[TabData] = field(factory=lambda: [TabData("references", "References")])
    references: list[str] = field(factory=list)
    dashboard_label: str = field(default="title of dashboard")
    references_icon: str = field(default="list")
    sidemenu_icon: str = field(default="layout-text-window-reverse")
    data_path: pt.Path | None = field(default=None)
    qrcode_url: str | None = field(default=None)
    qrcode_url_text: str = field(default="click here")
    logo_size: tuple[int, int] = field(default=(150, 100))
    logo_path: pt.Path | None = field(default=None)

    @classmethod
    def load(cls, path: pt.Path):
        if path.exists():
            with path.open("r") as ipf:
                data = json.load(ipf)
            return cattr.structure(data, cls)
        else:
            return cls()

    def save(self, path):
        data = cattr.unstructure(self)
        with path.open("w") as opf:
            json.dump(data, opf)

    def prepare(self, tab_hooks):
        if self.enable_references:
            if "references" not in [i.id for i in self.tabs]:
                self.tabs.append(
                    TabData("references", "References", self.references_icon)
                )

        if "contacts" not in [i.id for i in self.tabs]:
            self.tabs.append(TabData("contacts", "Information", "chat-square-dots"))

        for itab in self.tabs:
            if itab.id in tab_hooks:
                itab.tab_ref = tab_hooks[itab.id]
            itab.display_infobox = True
            if itab.text is None and itab.path is None:
                itab.display_infobox = False
            elif itab.path is not None and not itab.path.exists():
                itab.display_infobox = False


def load_plots_config(path: pt.Path):
    plots_cfg = collections.defaultdict(dict)
    for ifile in path.glob("*.json"):
        cfg_data = json.load(ifile.open("r"))
        plots_cfg[ifile.stem] = cfg_data
    return plots_cfg
