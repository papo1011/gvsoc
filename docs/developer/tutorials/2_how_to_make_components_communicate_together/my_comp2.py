
import gvsoc.systree


class MyComp2(gvsoc.systree.Component):

    def __init__(self, parent: gvsoc.systree.Component, name: str):

        super().__init__(parent, name)

        self.add_sources(['my_comp2.cpp'])

    def i_NOTIF(self) -> gvsoc.systree.SlaveItf:
        return gvsoc.systree.SlaveItf(self, 'notif', signature='wire<bool>')

    def o_RESULT(self, itf: gvsoc.systree.SlaveItf):
        self.itf_bind('result', itf, signature='wire<MyResult>')